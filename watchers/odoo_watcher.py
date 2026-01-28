#!/usr/bin/env python3
"""
Odoo Watcher - Monitor Odoo Accounting for Events

Monitors Odoo Community Edition for accounting events:
- New invoices (customer)
- New vendor bills
- Payments received
- Overdue invoices

Usage:
    python -m watchers.odoo_watcher --vault AI_Employee_Vault --interval 300
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher
from watchers.error_recovery import with_retry
from utils.odoo_client import OdooClient, AuthenticationError, ConnectionError as OdooConnectionError


class OdooWatcher(BaseWatcher):
    """
    Monitor Odoo Accounting for events.

    This watcher connects to Odoo via the Odoo MCP server and monitors
    for accounting events that require human attention.
    """

    def __init__(
        self,
        vault_path: str,
        odoo_url: str = "http://localhost:8069",
        odoo_db: str = "odoo",
        odoo_username: str = "admin",
        odoo_password: str = "admin",
        check_interval: int = 300,
        dry_run: bool = False,
    ):
        super().__init__(vault_path, check_interval, dry_run)
        self.odoo_url = odoo_url
        self.odoo_db = odoo_db
        self.odoo_username = odoo_username
        self.odoo_password = odoo_password

        # Create Odoo client
        self.odoo_client = OdooClient(
            url=odoo_url,
            database=odoo_db,
            username=odoo_username,
            password=odoo_password,
        )

        # Track last check time
        self.last_check = None
        self.state_file = self.vault_path / ".odoo_watcher_state.json"
        self._load_state()

        # Accounting data path
        self.accounting_path = self.vault_path / "Accounting"
        self.accounting_path.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Odoo Watcher initialized for {odoo_url}")

    def _load_state(self) -> None:
        """Load watcher state from file."""
        if self.state_file.exists():
            try:
                import json
                state = json.loads(self.state_file.read_text())
                self.last_check = datetime.fromisoformat(state.get("last_check"))
                self.logger.info(f"Loaded state: last check was {self.last_check}")
            except Exception as e:
                self.logger.warning(f"Could not load state: {e}")

    def _save_state(self) -> None:
        """Save watcher state to file."""
        try:
            import json
            state = {
                "last_check": self.last_check.isoformat() if self.last_check else None,
                "updated_at": datetime.now().isoformat(),
            }
            self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        except Exception as e:
            self.logger.warning(f"Could not save state: {e}")

    def _connect_to_odoo(self) -> bool:
        """
        Connect to Odoo server.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.odoo_client.connect()
            self.logger.info("Connected to Odoo successfully")
            return True
        except AuthenticationError as e:
            self.logger.error(f"Odoo authentication failed: {e}")
            return False
        except OdooConnectionError as e:
            self.logger.warning(f"Odoo not available: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to Odoo: {e}")
            return False

    @with_retry(max_attempts=3, base_delay=2, max_delay=60)
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new accounting events in Odoo.

        Returns:
            List of new accounting events requiring attention
        """
        self.logger.info("Checking Odoo for accounting updates...")

        events = []
        now = datetime.now()

        # Try to connect to Odoo
        if not self._connect_to_odoo():
            # Odoo not available, return empty list
            self.last_check = now
            self._save_state()
            return []

        try:
            # Check for events since last check (or last 24 hours on first run)
            since = self.last_check or (now - timedelta(hours=24))
            date_from_str = since.strftime("%Y-%m-%d")

            # Check for draft invoices (need to be sent)
            draft_invoices = self.odoo_client.get_invoices(
                state="draft", date_from=date_from_str, limit=50
            )
            for inv in draft_invoices:
                events.append({
                    "type": "invoice",
                    "id": inv["name"],
                    "partner": inv["partner_name"],
                    "amount": inv["amount_total"],
                    "date": inv["date"],
                    "due_date": inv["due_date"],
                    "state": inv["state"],
                })

            # Check for new payments
            payments = self.odoo_client.get_payments(
                date_from=date_from_str, limit=50
            )
            for pay in payments:
                if pay["state"] == "posted":
                    events.append({
                        "type": "payment",
                        "id": pay["name"],
                        "partner": pay["partner_name"],
                        "amount": pay["amount"],
                        "date": pay["date"],
                        "state": pay["state"],
                    })

            # Check for overdue invoices
            overdue = self.odoo_client.get_overdue_invoices(days_overdue=1, limit=50)
            for inv in overdue:
                events.append({
                    "type": "overdue_invoice",
                    "id": inv["name"],
                    "partner": inv["partner_name"],
                    "amount": inv["amount_residual"],
                    "date": inv["date"],
                    "due_date": inv["due_date"],
                    "state": inv["payment_state"],
                })

        except Exception as e:
            self.logger.error(f"Error fetching Odoo data: {e}")

        self.last_check = now
        self._save_state()

        self.logger.info(f"Found {len(events)} new accounting events")
        return events

    def create_action_file(self, event: Dict[str, Any]) -> Optional[Path]:
        """
        Create an action file for an accounting event.

        Args:
            event: Accounting event from Odoo

        Returns:
            Path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_type = event.get("type", "unknown").upper()

        filename = f"ODOO_{event_type}_{event.get('id', timestamp)}_{timestamp}.md"
        filepath = self.needs_action / filename

        # Build the action file content
        content = f"""---
type: odoo_{event.get('type', 'event')}
service: odoo
priority: {self._get_priority(event)}
status: pending
created: {datetime.now().isoformat()}
odoo_id: {event.get('id')}
odoo_type: {event.get('type')}
---

# Odoo {event.get('type', 'Event').title()}: {event.get('id', 'Unknown')}

**Partner:** {event.get('partner', 'Unknown')}
**Amount:** ${event.get('amount', 0):,.2f}
**Date:** {event.get('date', 'Unknown')}
**Status:** {event.get('state', 'unknown').title()}

"""

        if event.get('type') == 'invoice':
            content += f"""
## Customer Invoice

**Due Date:** {event.get('due_date', 'Not set')}

### Suggested Actions:
- [ ] Review invoice details
- [ ] Send to customer if not already sent
- [ ] Record payment when received
- [ ] Reconcile with bank statement

### Priority: {self._get_priority_description(event)}
"""

        elif event.get('type') == 'payment':
            content += f"""
## Payment Received

### Suggested Actions:
- [ ] Verify payment amount
- [ ] Reconcile with invoice
- [ ] Update customer records
- [ ] Generate receipt if needed

### Priority: High
"""

        elif event.get('type') == 'vendor_bill':
            content += f"""
## Vendor Bill

**Due Date:** {event.get('due_date', 'Not set')}
**Vendor:** {event.get('partner', 'Unknown')}

### Suggested Actions:
- [ ] Review bill details
- [ ] Approve for payment
- [ ] Schedule payment
- [ ] Update expense records

### Priority: {self._get_priority_description(event)}
"""

        content += f"""
---
*Detected by Odoo Watcher on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Odoo URL: {self.odoo_url}*
"""

        if self.dry_run:
            self.logger.info(f"DRY RUN: Would create {filepath}")
            return None

        try:
            filepath.write_text(content, encoding="utf-8")
            self.logger.info(f"Created action file: {filepath.name}")

            # Log the action
            self._log_audit_action("odoo_event_detected", {
                "event_type": event.get("type"),
                "event_id": event.get("id"),
                "partner": event.get("partner"),
                "amount": event.get("amount"),
            })

            return filepath
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}")
            return None

    def get_item_id(self, event: Dict[str, Any]) -> str:
        """
        Get unique identifier for an event.

        Args:
            event: Accounting event

        Returns:
            Unique ID string
        """
        return f"{event.get('type', 'unknown')}_{event.get('id', 'unknown')}"

    def _get_priority(self, event: Dict[str, Any]) -> str:
        """Determine priority level for an event."""
        # High priority for overdue or large amounts
        if event.get('type') == 'invoice':
            amount = event.get('amount', 0)
            if amount > 5000:
                return "high"
            elif amount > 1000:
                return "medium"
            else:
                return "low"
        elif event.get('type') == 'payment':
            return "high"
        else:
            return "medium"

    def _get_priority_description(self, event: Dict[str, Any]) -> str:
        """Get human-readable priority description."""
        priority = self._get_priority(event)
        descriptions = {
            "high": "🔴 Requires immediate attention",
            "medium": "🟠 Review within 24 hours",
            "low": "🟢 Can be handled this week",
        }
        return descriptions.get(priority, "🟢 Normal priority")

    def _log_audit_action(self, action_type: str, parameters: dict) -> None:
        """Log action to audit log."""
        try:
            from utils.audit_logging import AuditLogger
            audit_logger = AuditLogger(self.vault_path)
            audit_logger.log_action(
                action_type=action_type,
                target="odoo",
                parameters=parameters,
                result="success"
            )
        except Exception as e:
            self.logger.warning(f"Could not log audit action: {e}")

    def update_accounting_file(self) -> None:
        """
        Update the monthly accounting file with latest data from Odoo.

        This creates/updates the Accounting/YYYY-MM.md file with:
        - Revenue summary
        - Expenses summary
        - Invoice list
        - Payment list
        """
        try:
            now = datetime.now()
            month_start = now.replace(day=1)
            month_end_str = month_start.strftime("%Y-%m-%d")

            month_file = self.accounting_path / f"{now.strftime('%Y-%m')}.md"

            # Initialize accounting data
            accounting_data = {
                "revenue": 0.0,
                "expenses": 0.0,
                "invoices_sent": [],
                "invoices_overdue": [],
                "payments_received": [],
                "vendor_bills": [],
            }

            # Try to connect to Odoo and fetch real data
            odoo_connected = self._connect_to_odoo()

            if odoo_connected:
                self.logger.info("Fetching live accounting data from Odoo...")

                try:
                    # Get revenue from posted customer invoices
                    accounting_data["revenue"] = self.odoo_client.get_revenue(
                        date_from=month_end_str, date_to=now.strftime("%Y-%m-%d")
                    )

                    # Get expenses from posted vendor bills
                    accounting_data["expenses"] = self.odoo_client.get_expenses(
                        date_from=month_end_str, date_to=now.strftime("%Y-%m-%d")
                    )

                    # Get all invoices this month
                    all_invoices = self.odoo_client.get_invoices(
                        date_from=month_end_str, limit=200
                    )
                    for inv in all_invoices:
                        if inv["state"] == "posted":
                            accounting_data["invoices_sent"].append(inv)
                        # Only add to overdue if not paid AND past due date
                        if inv["payment_state"] not in ["paid", "reversed"]:
                            # Check if invoice is actually overdue (due date has passed)
                            try:
                                due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d")
                                # Compare dates only (ignore time)
                                if due_date.date() < now.date():
                                    accounting_data["invoices_overdue"].append(inv)
                            except (ValueError, KeyError):
                                # If we can't parse the due date, skip it
                                pass

                    # Get payments this month
                    payments = self.odoo_client.get_payments(
                        date_from=month_end_str, limit=200
                    )
                    accounting_data["payments_received"] = [
                        p for p in payments if p["payment_type"] == "inbound"
                    ]

                    # Get vendor bills
                    vendor_bills = self.odoo_client.get_vendor_bills(
                        date_from=month_end_str, limit=200
                    )
                    accounting_data["vendor_bills"] = [
                        bill for bill in vendor_bills if bill["state"] == "posted"
                    ]

                except Exception as e:
                    self.logger.error(f"Error fetching Odoo data: {e}")
                    # Use placeholder data if fetch fails
            else:
                self.logger.info("Odoo not available - using placeholder data")

            # Build the accounting file content
            content = self._build_accounting_content(now, accounting_data, odoo_connected)

            if not month_file.exists():
                month_file.write_text(content, encoding="utf-8")
                self.logger.info(f"Created accounting file: {month_file.name}")
            else:
                # Update existing file with new data
                month_file.write_text(content, encoding="utf-8")
                self.logger.info(f"Updated accounting file: {month_file.name}")

        except Exception as e:
            self.logger.error(f"Error updating accounting file: {e}")

    def _build_accounting_content(self, now: datetime, data: dict, odoo_connected: bool) -> str:
        """Build accounting file content from data."""
        month_start = now.replace(day=1)
        next_month = month_start + timedelta(days=32)
        month_end = next_month.replace(day=1) - timedelta(days=1)

        # Build invoices table
        invoices_table = "| Invoice # | Client | Amount | Date | Status |\n|-----------|--------|--------|------|--------|\n"
        for inv in data.get("invoices_sent", [])[:10]:
            invoices_table += f"| {inv['name']} | {inv['partner_name']} | ${inv['amount_total']:,.2f} | {inv['date']} | {inv['payment_state'].title()} |\n"

        if not data.get("invoices_sent"):
            invoices_table += "| *No invoices sent* | - | - | - | - |\n"

        # Build overdue table
        overdue_table = "| Invoice # | Client | Amount | Due Date | Days Overdue |\n|-----------|--------|--------|----------|-------------|\n"
        for inv in data.get("invoices_overdue", [])[:10]:
            try:
                due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
                days_overdue = (datetime.now() - due).days
            except:
                days_overdue = 0

            overdue_table += f"| {inv['name']} | {inv['partner_name']} | ${inv['amount_residual']:,.2f} | {inv['due_date']} | {days_overdue} |\n"

        if not data.get("invoices_overdue"):
            overdue_table += "| *No overdue invoices* | - | - | - | - |\n"

        # Source note
        source_note = "Odoo Live Data" if odoo_connected else "Odoo (Not Connected - Placeholder)"
        net_profit = data["revenue"] - data["expenses"]

        content = f"""---
month: {now.strftime('%Y-%m')}
period_start: {month_start.strftime('%Y-%m-%d')}
period_end: {month_end.strftime('%Y-%m-%d')}
status: open
updated: {now.isoformat()}
source: odoo_watcher
odoo_connected: {str(odoo_connected).lower()}
---

# Accounting: {now.strftime('%B %Y')}

## Revenue
| Source | Amount | Invoices | Notes |
|--------|--------|----------|-------|
| Customer Invoices | ${data['revenue']:,.2f} | {len(data['invoices_sent'])} | {source_note} |

**Total Revenue:** ${data['revenue']:,.2f}

## Expenses
| Category | Amount | Vendor |
|----------|--------|--------|
| Vendor Bills | ${data['expenses']:,.2f} | {len(data['vendor_bills'])} vendors |

**Total Expenses:** ${data['expenses']:,.2f}

## Invoices

### Sent
{invoices_table}

### Overdue
{overdue_table}

## Payments Received
| Payment # | Client | Amount | Date | Status |
|-----------|--------|--------|------|--------|
"""

        for pay in data.get("payments_received", [])[:10]:
            payments_table = f"| {pay['name']} | {pay['partner_name']} | ${pay['amount']:,.2f} | {pay['date']} | {pay['state'].title()} |\n"
            content += payments_table

        if not data.get("payments_received"):
            content += "| *No payments received* | - | - | - | - |\n"

        content += f"""
## Profit & Loss
- **Revenue:** ${data['revenue']:,.2f}
- **Expenses:** ${data['expenses']:,.2f}
- **Net Profit:** ${net_profit:,.2f}

## Notes
*Accounting file updated by Odoo Watcher via XML-RPC*
*Odoo Status: {'Connected' if odoo_connected else 'Not Connected'}*
*Data Source: Odoo Community Edition at {self.odoo_url}*

---
*Last updated: {now.isoformat()}*
"""

        return content

    def run_once(self) -> None:
        """Run a single check and update accounting file."""
        self.logger.info("Running Odoo watcher (once mode)...")

        # Check for new events
        events = self.check_for_updates()

        # Create action files for each event
        for event in events:
            self.create_action_file(event)

        # Update accounting file
        self.update_accounting_file()

        self.logger.info("Odoo watcher check complete")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Odoo Accounting for events"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to the vault (default: AI_Employee_Vault)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without creating files"
    )
    parser.add_argument(
        "--odoo-url",
        default="http://localhost:8069",
        help="Odoo server URL (default: http://localhost:8069)"
    )
    parser.add_argument(
        "--odoo-db",
        default="odoo",
        help="Odoo database name (default: odoo)"
    )
    parser.add_argument(
        "--odoo-username",
        default="admin",
        help="Odoo username (default: admin)"
    )
    parser.add_argument(
        "--odoo-password",
        default="admin",
        help="Odoo password (default: admin)"
    )

    args = parser.parse_args()

    watcher = OdooWatcher(
        vault_path=args.vault,
        odoo_url=args.odoo_url,
        odoo_db=args.odoo_db,
        odoo_username=args.odoo_username,
        odoo_password=args.odoo_password,
        check_interval=args.interval,
        dry_run=args.dry_run,
    )

    if args.once:
        watcher.run_once()
    else:
        watcher.run()


if __name__ == "__main__":
    main()
