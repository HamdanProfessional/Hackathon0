"""
Xero Watcher - Monitors Xero accounting for transactions and invoices

This watcher connects to Xero API to monitor:
- New bank transactions
- Invoice status changes
- Payment status updates
- Client payment history

Setup:
1. Create Xero developer account at https://developer.xero.com/
2. Create a new app and get credentials
3. Save credentials to .xero_credentials.json
4. Run authenticate() once to authorize
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# Import from xero_python package (new package structure)
import xero_python
from xero_python.accounting import AccountingApi
from xero_python.api_client import ApiClient
from xero_python.identity import IdentityApi
from requests_oauthlib import OAuth2Session

from .base_watcher import BaseWatcher
from .error_recovery import with_retry, ErrorCategory
from .deduplication import Deduplication


# Xero API scopes (valid OAuth 2.0 scopes only)
SCOPES = [
    "accounting.transactions",
    "accounting.reports.read",
    "accounting.contacts",
    "offline_access",  # Required for refresh tokens
]


class XeroWatcher(BaseWatcher):
    """
    Watches Xero accounting system for financial activity.

    Monitors for:
    - New bank transactions
    - Invoice status changes
    - Overdue invoices
    - Revenue milestones
    """

    # Unusual expense threshold
    UNUSUAL_EXPENSE_THRESHOLD = 500

    # Invoice overdue days
    OVERDUE_DAYS = 7

    def __init__(
        self,
        vault_path: str,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        tenant_id: Optional[str] = None,
        check_interval: int = 3600,
        dry_run: bool = False,
    ):
        """
        Initialize the Xero Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Xero OAuth credentials.json
            token_path: Path to save/load token.json
            tenant_id: Xero tenant ID
            check_interval: Seconds between checks (default: 3600 = 1 hour)
            dry_run: If True, don't create files
        """
        super().__init__(vault_path, check_interval, dry_run)
        self.credentials_path = credentials_path or str(Path(vault_path) / ".xero_credentials.json")
        self.token_path = token_path or str(Path(vault_path) / ".xero_token.json")
        self.tenant_id = tenant_id
        self.xero_client = None
        self.accounting_path = self.vault_path / "Accounting"
        self.accounting_path.mkdir(parents=True, exist_ok=True)

        # Use persistent deduplication for Xero items
        self.dedup = Deduplication(
            vault_path=vault_path,
            state_file=".xero_state.json",
            item_prefix="XERO",
            scan_folders=True
        )

        # Load credentials and authenticate
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Xero API using OAuth 2.0."""
        # Load credentials
        if not os.path.exists(self.credentials_path):
            raise ValueError(
                f"Xero credentials not found at {self.credentials_path}. "
                "Please create a .xero_credentials.json file with your Xero app credentials."
            )

        with open(self.credentials_path, "r") as f:
            credentials = json.load(f)

        # Load or create token
        if os.path.exists(self.token_path):
            with open(self.token_path, "r") as f:
                token_data = json.load(f)

            # Refresh if expired
            if token_data.get("expires_at"):
                expires_at = datetime.fromtimestamp(token_data["expires_at"])
                if datetime.now() >= expires_at:
                    token_data = self._refresh_token(token_data, credentials)

            # Create Xero client with xero_python SDK
            from xero_python.api_client.configuration import Configuration
            from xero_python.api_client.oauth2 import OAuth2Token
            from xero_python import __version__ as xero_version
            print(f"Xero Python version: {xero_version}")

            # Store token data for refresh
            self.token_data = token_data
            self.credentials = credentials

            # Create proper Configuration object
            config = Configuration(
                debug=False,
                oauth2_token=OAuth2Token(
                    client_id=credentials["clientId"],
                    client_secret=credentials["clientSecret"],
                ),
            )

            self.xero_client = ApiClient(config)

            # Register token saver
            @self.xero_client.oauth2_token_saver
            def save_token(token):
                """Save token to file."""
                token["tenant_id"] = self.token_data.get("tenant_id", "")
                token["tenant_name"] = self.token_data.get("tenant_name", "")
                with open(self.token_path, "w", encoding='utf-8') as f:
                    json.dump(token, f, indent=2)
                self.token_data = token

            # Set token on client
            self.xero_client.set_oauth2_token(token_data)

            self.tenant_id = token_data.get("tenant_id")
            if not self.tenant_id:
                raise ValueError("tenant_id not found in token file. Please re-authenticate.")

            self.logger.info("Xero API authenticated successfully via xero_python")

        else:
            # Need to run OAuth flow
            raise ValueError(
                "Xero token not found. Please run authenticate() first."
            )

    def _refresh_token(self, token_data: dict, credentials: dict) -> dict:
        """Refresh expired OAuth token."""
        session = OAuth2Session(
            client_id=credentials["clientId"],
            token=token_data,
        )

        token = session.refresh_token(
            "https://identity.xero.com/connect/token",
            client_secret=credentials["clientSecret"],
            refresh_token=token_data["refresh_token"],
        )

        # Save new token
        with open(self.token_path, "w") as f:
            json.dump(token, f, indent=2)

        return token

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new accounting activity.

        Returns:
            List of new items (transactions, invoices, alerts)
        """
        updates = []

        try:
            # Check for new transactions
            transactions = self._get_new_transactions()
            updates.extend(transactions)

            # Check for invoice status changes
            invoices = self._get_invoice_updates()
            updates.extend(invoices)

            # Check for overdue invoices
            overdue = self._get_overdue_invoices()
            updates.extend(overdue)

            # Update monthly accounting file
            self._update_monthly_accounting()

        except Exception as e:
            self.logger.error(f"Error checking Xero updates: {e}")
            self.log_action("error", {"error": str(e)})

        return updates

    def _get_new_transactions(self) -> List[Dict[str, Any]]:
        """Get new bank transactions since last check."""
        try:
            # Get transactions from last 24 hours
            since_date = datetime.now() - timedelta(days=1)

            # Query transactions (using Xero API)
            # Note: Actual API call depends on your Xero setup
            # This is a simplified example

            transactions = []  # self.xero_client.banktransactions.filter(...)

            # Process transactions
            new_transactions = []
            for txn in transactions:
                # Check if unusual expense
                is_unusual = (
                    txn.get("Type") == "RECEIVE-SPEND"
                    and abs(txn.get("Amount", 0)) > self.UNUSUAL_EXPENSE_THRESHOLD
                )

                if is_unusual or any(
                    kw in txn.get("Description", "").lower()
                    for kw in ["invoice", "payment", "subscription"]
                ):
                    new_transactions.append({
                        "id": f"XERO_TXN_{txn['BankTransactionID']}",
                        "type": "transaction",
                        "date": txn.get("Date"),
                        "amount": txn.get("Amount"),
                        "description": txn.get("Description"),
                        "is_unusual": is_unusual,
                    })

            return new_transactions

        except Exception as e:
            self.logger.error(f"Error fetching transactions: {e}")
            return []

    def _get_invoice_updates(self) -> List[Dict[str, Any]]:
        """Get invoices with recent status changes."""
        try:
            # Get invoices updated in last 24 hours
            since_date = datetime.now() - timedelta(days=1)

            invoices = []  # self.xero.client.invoices.filter(...)

            updates = []
            for invoice in invoices:
                status = invoice.get("Status")
                invoice_no = invoice.get("InvoiceNumber")

                # Check for status changes
                if status == "PAID":
                    updates.append({
                        "id": f"XERO_INV_{invoice_no}",
                        "type": "invoice_paid",
                        "invoice_number": invoice_no,
                        "amount": invoice.get("Total"),
                        "contact": invoice.get("Contact", {}).get("Name"),
                        "date_paid": invoice.get("FullyPaidOnDate"),
                    })
                elif status == "SENT":
                    updates.append({
                        "id": f"XERO_INV_{invoice_no}",
                        "type": "invoice_sent",
                        "invoice_number": invoice_no,
                        "amount": invoice.get("Total"),
                        "contact": invoice.get("Contact", {}).get("Name"),
                        "due_date": invoice.get("DueDate"),
                    })

            return updates

        except Exception as e:
            self.logger.error(f"Error fetching invoice updates: {e}")
            return []

    def _get_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Get invoices that are overdue."""
        try:
            overdue_date = datetime.now() - timedelta(days=self.OVERDUE_DAYS)

            # Get overdue invoices
            invoices = []  # self.xero.invoices.filter(...)

            overdue = []
            for invoice in invoices:
                due_date = datetime.fromisoformat(invoice.get("DueDate"))
                if due_date < overdue_date and invoice.get("Status") not in ["PAID", "VOIDED"]:
                    overdue.append({
                        "id": f"XERO_OVERDUE_{invoice['InvoiceNumber']}",
                        "type": "invoice_overdue",
                        "invoice_number": invoice.get("InvoiceNumber"),
                        "amount": invoice.get("AmountDue"),
                        "contact": invoice.get("Contact", {}).get("Name"),
                        "due_date": invoice.get("DueDate"),
                        "days_overdue": (datetime.now() - due_date).days,
                    })

            return overdue

        except Exception as e:
            self.logger.error(f"Error fetching overdue invoices: {e}")
            return []

    def _update_monthly_accounting(self) -> None:
        """Update the monthly accounting file."""
        month_file = self.accounting_path / datetime.now().strftime("%Y-%m.md")

        if not month_file.exists():
            # Create new monthly file
            content = self._generate_monthly_accounting_content()
            if not self.dry_run:
                month_file.write_text(content, encoding="utf-8")
                self.logger.info(f"Created monthly accounting file: {month_file.name}")
        else:
            # Update existing file
            self.logger.info(f"Monthly accounting file exists: {month_file.name}")

    def _generate_monthly_accounting_content(self) -> str:
        """Generate content for monthly accounting file."""
        month = datetime.now().strftime("%Y-%m")

        return f"""---
month: {month}
period_start: {month}-01
period_end: {month}-31
status: open
---

# Accounting: {month}

## Revenue
| Source | Amount | Invoices | Notes |
|--------|--------|----------|-------|
| *Updated by Xero Watcher* | $0.00 | 0 | - |

**Total Revenue:** $0.00

## Expenses
| Category | Amount | Vendor |
|----------|--------|--------|
| *Updated by Xero Watcher* | $0.00 | - |

**Total Expenses:** $0.00

## Invoices

### Sent
| Invoice # | Client | Amount | Date | Status |
|-----------|--------|--------|------|--------|
| *Updated by Xero Watcher* | - | - | - | - |

### Overdue
| Invoice # | Client | Amount | Due Date | Days Overdue |
|-----------|--------|--------|----------|-------------|
| *Updated by Xero Watcher* | - | - | - | - |

## Profit & Loss
- **Revenue:** $0.00
- **Expenses:** ($0.00)
- **Net Profit:** $0.00

## Notes
*Accounting file created by Xero Watcher. Updates automatically.*

---

*Last updated: {datetime.now().isoformat()}*
"""

    def get_item_id(self, item: Dict[str, Any]) -> str:
        """Get unique ID for an accounting item."""
        return item["id"]

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create an action file for accounting items needing attention.

        Args:
            item: Accounting item from check_for_updates()

        Returns:
            Path to created file, or None
        """
        item_type = item["type"]
        item_id = item["id"]

        # Check if already processed using persistent deduplication
        if self.dedup.is_processed(item_id):
            self.logger.info(f"Xero item {item_id} already processed, skipping")
            return None

        # Mark as processed immediately to prevent race conditions
        self.dedup.mark_processed(item_id)

        # Only create action files for important items
        if item_type in ["invoice_overdue", "transaction_unusual"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{item_type.upper()}_{timestamp}.md"
            filepath = self.needs_action / filename

            if item_type == "invoice_overdue":
                content = self._create_overdue_invoice_content(item)
            elif item_type == "transaction_unusual":
                content = self._create_unusual_transaction_content(item)
            else:
                return None

            if not self.dry_run:
                filepath.write_text(content, encoding="utf-8")
                self.logger.info(f"Created action file: {filepath.name}")
                return filepath

        return None

    def _create_overdue_invoice_content(self, item: Dict[str, Any]) -> str:
        """Create content for overdue invoice alert."""
        return f"""---
type: invoice_overdue
source: xero
invoice_number: {item['invoice_number']}
amount: ${item['amount']}
contact: {item['contact']}
due_date: {item['due_date']}
days_overdue: {item['days_overdue']}
priority: high
status: pending
created: {datetime.now().isoformat()}
---

# Overdue Invoice Alert

**Invoice:** {item['invoice_number']}
**Client:** {item['contact']}
**Amount:** ${item['amount']}
**Due Date:** {item['due_date']}
**Days Overdue:** {item['days_overdue']}

## Action Required

- [ ] Send payment reminder to client
- [ ] Follow up via phone/email
- [ ] Update Company_Handbook if this is a repeat issue

## Suggested Message

Subject: Payment Reminder: Invoice {item['invoice_number']}

Hi {item['contact']},

This is a friendly reminder that invoice {item['invoice_number']} for ${item['amount']} is now {item['days_overdue']} days overdue.

Please let us know if you have any questions or need a copy of the invoice.

Best regards

---

*Created by Xero Watcher*
"""

    def _create_unusual_transaction_content(self, item: Dict[str, Any]) -> str:
        """Create content for unusual transaction alert."""
        return f"""---
type: unusual_expense
source: xero
amount: ${item['amount']}
description: {item['description']}
date: {item['date']}
priority: medium
status: pending
created: {datetime.now().isoformat()}
---

# Unusual Expense Alert

**Amount:** ${item['amount']}
**Description:** {item['description']}
**Date:** {item['date']}

## Review Required

This expense exceeds the usual threshold (${self.UNUSUAL_EXPENSE_THRESHOLD}).

## Questions
- [ ] Is this a legitimate business expense?
- [ ] Should this be categorized differently?
- [ ] Does this require updating the budget?

## Notes

<!-- Add your review notes here -->

---

*Created by Xero Watcher*
"""


def authenticate(credentials_path: str, token_path: str) -> None:
    """
    Run the OAuth flow to authenticate with Xero.

    Call this once to set up credentials.

    Args:
        credentials_path: Path to Xero credentials.json
        token_path: Where to save the access token
    """
    # Load credentials
    with open(credentials_path, "r") as f:
        credentials = json.load(f)

    # Create OAuth session (client_secret is used when fetching token, not here)
    session = OAuth2Session(
        client_id=credentials["clientId"],
        scope=SCOPES,
        redirect_uri=credentials.get("redirectUri", "http://localhost:3000/callback"),
    )

    # Get authorization URL
    auth_url, state = session.authorization_url(
        "https://login.xero.com/identity/connect/authorize"
    )

    print("\n" + "=" * 60)
    print("XERO OAUTH AUTHENTICATION")
    print("\n" + "=" * 60)
    print("\n1. Please visit this URL to authorize:")
    print(f"   {auth_url}")
    print("\n2. Log in to Xero (if not already logged in)")
    print("3. Select your organization/tenant")
    print("\n4. After authorization, you'll be redirected to localhost:3000/callback")
    print("\n5. Copy the full callback URL and paste it below:\n")

    # Get callback URL with code
    callback_url = input("Enter the full callback URL: ")

    # Fetch token
    try:
        token = session.fetch_token(
            "https://identity.xero.com/connect/token",
            client_secret=credentials["clientSecret"],
            authorization_response=callback_url,
        )

        # Get tenants
        print("\n✅ Authentication successful!")
        print(f"Token received, expires: {token.get('expires_at', 'unknown')}")

        # Save token
        with open(token_path, "w", encoding='utf-8') as f:
            json.dump(token, f, indent=2)

        print(f"✅ Token saved to: {token_path}")

        # Now get the tenant ID
        print("\n" + "=" * 60)
        print("GETTING TENANT ID")
        print("\n" + "=" * 60)
        print("\n⚠️  IMPORTANT: You also need your XERO_TENANT_ID!")
        print("   1. Log in to Xero")
        print("   2. Go to: https://my.xero.com/Settings/Organization Settings")
        print("   3. Your Tenant ID is in the URL (e.g., xyz123abc)")
        print("\n   Enter your Tenant ID below or press Enter if you have it:")

        tenant_id = input("Enter Xero Tenant ID (or press Enter to skip): ").strip()

        if tenant_id:
            # Save tenant_id to token for future use
            with open(token_path, "r+") as f:
                token_data = json.load(f)
            token_data["tenant_id"] = tenant_id
            f.seek(0)
            json.dump(token_data, f, indent=2)
            print(f"✅ Tenant ID saved to: {token_path}")
        else:
            print(f"\n⚠️  No tenant ID provided. You'll need to add it manually to {token_path}")
            print('   Add this to your token file: "tenant_id": "YOUR_TENANT_ID"')

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your credentials.json has correct client_id and client_secret")
        print("2. Check that your Xero app has the correct OAuth scopes enabled")
        print("3. Ensure redirect URI matches your Xero app settings")

    print(f"\n" + "=" * 60)
    print(f"After setup, restart the watcher:")
    print("  pm2 restart xero-watcher")
    print("\n" + "=" * 60 + "\n")


def main():
    """Entry point for running the Xero watcher directly."""
    import argparse

    parser = argparse.ArgumentParser(description="Xero Watcher for Personal AI Employee")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault (default: current directory)"
    )
    parser.add_argument(
        "--credentials",
        help="Path to Xero credentials.json"
    )
    parser.add_argument(
        "--token",
        help="Path to save/load token.json"
    )
    parser.add_argument(
        "--tenant-id",
        help="Xero tenant ID"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Check interval in seconds (default: 3600)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without creating files"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )
    parser.add_argument(
        "--authenticate",
        action="store_true",
        help="Run OAuth authentication flow"
    )

    args = parser.parse_args()

    if args.authenticate:
        # Set default paths based on vault if not provided
        vault_path = Path(args.vault)

        # Fix Windows path handling
        if not args.credentials:
            args.credentials = str(vault_path / ".xero_credentials.json")
        if not args.token:
            args.token = str(vault_path / ".xero_token.json")

        # Check if credentials file exists
        if not os.path.exists(args.credentials):
            print(f"\n❌ Credentials file not found: {args.credentials}")
            print(f"   Expected location: {args.credentials}")
            print(f"\nPlease ensure {args.credentials} exists with your Xero app credentials.")
            return

        # Check if credentials file has real credentials (not placeholders)
        with open(args.credentials, "r") as f:
            creds = json.load(f)
            if "your_xero_client_id" in creds.get("clientId", ""):
                print(f"\n❌ You still have placeholder credentials in {args.credentials}")
                print(f"   Please update with your real Xero credentials:")
                print(f"   clientId: YOUR_REAL_CLIENT_ID")
                print(f"   clientSecret: YOUR_REAL_CLIENT_SECRET")
                return

        authenticate(args.credentials, args.token)
        return

    watcher = XeroWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token,
        tenant_id=args.tenant_id,
        check_interval=args.interval,
        dry_run=args.dry_run,
    )

    if args.once:
        items = watcher.run_once()
        print(f"Found {len(items)} accounting updates")
        for item in items:
            print(f"  - {item['type']}: {item.get('description', item.get('invoice_number', 'N/A'))}")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
