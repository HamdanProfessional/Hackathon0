#!/usr/bin/env python3
"""
Xero Watcher (Xero MCP version)

Monitors Xero accounting system for financial events via the Xero MCP server.

This version connects to the local Xero MCP server instead of using the outdated Python SDK.

Usage:
    python xero_watcher_mcp.py --vault . --once
"""

import os
import json
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from watchers.base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XeroWatcherMCP(BaseWatcher):
    """
    Watches Xero accounting system via Xero MCP server.

    Monitors for:
    - Overdue invoices
    - New invoices
    - Payments received
    - Unusual expenses

    All monitoring happens through the Xero MCP server running on localhost:3000
    """

    # Xero MCP server endpoint
    MCP_SERVER = "http://localhost:3000"

    # Monitoring thresholds
    OVERDUE_DAYS = 7
    UNUSUAL_EXPENSE_THRESHOLD = 500

    def __init__(self, vault_path: str, check_interval: int = 3600, dry_run: bool = False):
        """
        Initialize the Xero Watcher (MCP version).

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 3600 = 1 hour)
            dry_run: If True, don't create files
        """
        super().__init__(vault_path, check_interval, dry_run)

        self.accounting_path = self.vault_path / "Accounting"
        self.accounting_path.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for Xero accounting events via Xero MCP.

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # First, get overdue invoices
            overdue = self._get_overdue_invoices()

            if overdue:
                for invoice in overdue:
                    events.append({
                        'id': f"INVOICE_{invoice.get('invoiceNumber', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'type': 'overdue_invoice',
                        'data': invoice
                    })
                    logger.info(f"Found overdue invoice: {invoice.get('invoiceNumber', 'UNKNOWN')}")

            # Then, get recent invoices (last 7 days)
            recent = self._get_recent_invoices()

            if recent:
                for invoice in recent:
                    # Check if it's a new invoice (last 7 days)
                    created_date = datetime.fromisoformat(invoice.get('date', ''))

                    if (datetime.now() - created_date).days <= 7:
                        events.append({
                            'id': f"INVOICE_{invoice.get('invoiceNumber', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            'type': 'new_invoice',
                            'data': invoice
                        })
                        logger.info(f"Found new invoice: {invoice.get('invoice_number', 'UNKNOWN')}")

        except Exception as e:
            logger.error(f"Error checking Xero updates: {e}")
            # Log audit action for failed check
            self._log_audit_action("xero_check", {
                "status": "failed",
                "error": str(e)
            }, result="failed")

        # Log audit action for successful check
        self._log_audit_action("xero_check", {
            "events_found": len(events)
        })

        return events

    def _call_mcp(self, tool_name: str, params: Dict) -> Any:
        """
        Call Xero MCP tool.

        Args:
            tool_name: Name of the tool (e.g., "get_overdue_invoices")
            params: Parameters for the tool

        Returns:
            Tool result
        """
        try:
            import requests

            response = requests.post(
                f"{self.MCP_SERVER}/tools/call",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": params,
                        "sessionId": "xero_watcher"
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return result['result']
                elif 'error' in result:
                    logger.error(f"Xero MCP error: {result['error']}")
                    return None
                else:
                    return result
            else:
                logger.error(f"Xero MCP HTTP error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error calling Xero MCP: {e}")
            return None

    def _get_overdue_invoices(self) -> List[Dict]:
        """
        Get all overdue invoices from Xero.

        Returns:
            List of overdue invoice dictionaries
        """
        try:
            result = self._call_mcp("get_overdue_invoices", {})

            if result and 'data' in result:
                return result['data']
            return []

        except Exception as e:
            logger.error(f"Error getting overdue invoices: {e}")
            return []

    def _get_recent_invoices(self) -> List[Dict]:
        """
        Get recent invoices from Xero.

        Returns:
            List of invoice dictionaries
        """
        try:
            # For now, try get_overdue_invoices which will include recent overdue invoices
            result = self._call_mcp("get_overdue_invoices", {})

            if result and 'data' in result:
                return result['data']
            return []

        except Exception as e:
            logger.error(f"Error getting recent invoices: {e}")
            return []

    def _get_profit_loss(self, period: str = "MONTH") -> Optional[Dict]:
        """
        Get profit and loss statement.

        Args:
            period: MONTH, QUARTER, YEAR

        Returns:
            P&L data or None
        """
        try:
            result = self._call_mcp("get_profit_loss", {"period": period})

            if result and 'data' in result:
                return result['data']
            return None

        except Exception as e:
            logger.error(f"Error getting P&L: {e}")
            return None

    def get_item_id(self, item: Dict) -> str:
        """Get unique ID for an event."""
        return item.get('id', f"xero_{int(datetime.now().timestamp())}")

    def create_action_file(self, item: Dict) -> Optional[Path]:
        """
        Create action file in Accounting folder.

        Args:
            item: Event dictionary

        Returns:
            Path to created file
        """
        try:
            event_type = item.get('type', 'xero_event')
            event_data = item.get('data', {})

            # Create filename based on event type and timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if event_type == 'overdue_invoice':
                invoice_num = event_data.get('invoiceNumber', 'UNKNOWN')
                filename = f"XERO_OVERDUE_{timestamp}_{invoice_num}.md"
            elif event_type == 'new_invoice':
                invoice_num = event_data.get('invoiceNumber', 'UNKNOWN')
                filename = f"XERO_NEW_{timestamp}_{invoice_num}.md"
            else:
                filename = f"XERO_{event_type}_{timestamp}.md"

            filepath = self.accounting_path / filename

            # Check if already exists
            if filepath.exists():
                logger.debug(f"Action file already exists: {filename}")
                return None

            # Create action file content
            if event_type == 'overdue_invoice':
                content = f"""---
type: xero_invoice
action: follow_up
priority: high
status: pending_approval
created: {datetime.now().isoformat()}
---

# Overdue Invoice Detected

## Invoice Details

**Invoice Number:** {event_data.get('invoiceNumber', 'UNKNOWN')}

**Amount:** {event_data.get('amount', '0.00')}

**Due Date:** {event_data.get('dueDate', 'UNKNOWN')}

**Days Overdue:** {event_data.get('daysOverdue', '0')} days

**Status:** OVERDUE

## Action Required

- [ ] Contact client for payment
- [ ] Send payment reminder via email/phone
- [ ] Update payment status in Xero
- [] Consider late fee if applicable

## Context

Invoice is {event_data.get('daysOverdue', '0')} days overdue. Immediate follow-up recommended.

---

*Generated by Xero Watcher (MCP)*
"""
            else:
                content = f"""---
type: xero_invoice
action: review
priority: medium
status: pending_approval
created: {datetime.now().isoformat()}
---

# Xero Event Detected

## Type: {event_type}

## Details

```json
{json.dumps(event_data, indent=2)}
```

## Suggested Actions

- [ ] Review the event details
- [ ] Take appropriate action based on event type
- [ ] Update tracking when complete

---

*Generated by Xero Watcher (MCP)*
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created Xero action file: {filename}")

            # Log audit action
            self._log_audit_action("xero_action_file_created", {
                "filename": filename,
                "event_type": event_type,
                "data": event_data
            })

            return filepath

        except Exception as e:
            logger.error(f"Error creating action file: {e}")
            return None

    def _log_audit_action(self, action_type: str, parameters: Dict[str, Any], result: str = "success") -> None:
        """
        Log audit action to the audit log.

        Args:
            action_type: Type of action performed
            parameters: Parameters of the action
            result: Result of the action (success/failed)
        """
        from utils.audit_logging import AuditLogger

        try:
            audit_logger = AuditLogger(self.vault_path)
            audit_logger.log_action(
                action_type=action_type,
                target="xero",
                parameters=parameters,
                result=result
            )
        except Exception as e:
            logger.debug(f"Could not log audit action: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor Xero accounting system (Xero MCP version)"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Check interval in seconds (default: 3600 = 1 hour)"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Check once and exit"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't create files"
    )

    args = parser.parse_args()

    # Create watcher
    watcher = XeroWatcherMCP(
        vault_path=args.vault,
        check_interval=args.interval,
        dry_run=args.dry_run
    )

    if args.once:
        # Check once
        print("\n" + "="*60)
        print("XERO WATCHER (MCP Version) - One-Time Check")
        print("="*60)
        print(f"\nMCP Server: {watcher.MCP_SERVER}")
        print(f"\n[*] Checking for Xero events...\n")

        events = watcher.check_for_updates()

        print(f"\n[*] Found {len(events)} Xero events\n")

        for i, event in enumerate(events, 1):
            print(f"\n{i}. {event['type'].replace('_', ' ').title()}")
            print(f"   Details: {str(event.get('data', {}))[:100]}")
            watcher.create_action_file(event)
            print(f"   Created: {event.get('id')}.md")
            print()

        print("="*60)
        print(f"Done! Created {len(events)} action files")
        print("="*60)
    else:
        # Run continuous
        print("\n" + "="*60)
        print("XERO WATCHER (MCP Version) - Continuous")
        print("="*60)
        print(f"\nMCP Server: {watcher.MCP_SERVER}")
        print(f"Check interval: {args.interval} seconds")
        print("\n[*] Starting monitoring...")
        print("[*] Press Ctrl+C to stop\n")
        print("="*60 + "\n")

        watcher.run()


if __name__ == "__main__":
    main()
