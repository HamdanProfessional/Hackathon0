#!/usr/bin/env python3
"""
Odoo XML-RPC Client for AI Employee

Direct client for connecting to Odoo Community Edition via XML-RPC.
Used by Odoo Watcher to fetch accounting data.

Usage:
    from utils.odoo_client import OdooClient

    client = OdooClient(
        url="http://localhost:8069",
        database="odoo",
        username="admin",
        password="admin"
    )

    # Get invoices
    invoices = client.get_invoices(state="draft")

    # Get payments
    payments = client.get_payments()
"""

import xmlrpc.client
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class OdooClient:
    """Synchronous XML-RPC client for Odoo."""

    def __init__(
        self,
        url: str = "http://localhost:8069",
        database: str = "odoo",
        username: str = "admin",
        password: str = "admin",
    ):
        """
        Initialize Odoo XML-RPC client.

        Args:
            url: Odoo server URL (e.g., http://localhost:8069)
            database: Database name
            username: Odoo username
            password: Odoo password
        """
        self.url = url
        self.database = database
        self.username = username
        self.password = password

        # Clean up URL if needed
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            self.url = f"http://{url}"

        # XML-RPC endpoints
        self.common_endpoint = f"{self.url}/xmlrpc/2/common"
        self.object_endpoint = f"{self.url}/xmlrpc/2/object"

        # User ID after authentication
        self.uid = None
        self._connected = False

    def connect(self) -> int:
        """
        Connect to Odoo and authenticate user.

        Returns:
            int: Authenticated user ID

        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        try:
            common = xmlrpc.client.ServerProxy(self.common_endpoint)
            self.uid = common.authenticate(
                self.database, self.username, self.password, {}
            )

            if not self.uid:
                raise AuthenticationError(
                    f"Authentication failed for user '{self.username}'"
                )

            self._connected = True
            logger.info(f"Connected to Odoo as {self.username} (uid: {self.uid})")
            return self.uid

        except AuthenticationError:
            raise
        except Exception as e:
            raise ConnectionError(f"Error connecting to Odoo: {e}")

    def is_connected(self) -> bool:
        """Check if connected to Odoo."""
        return self._connected and self.uid is not None

    def _ensure_connected(self):
        """Ensure we are connected before executing operations."""
        if not self.is_connected():
            self.connect()

    def execute_kw(
        self,
        model: str,
        method: str,
        args: List = None,
        kwargs: Dict = None,
    ) -> Any:
        """
        Execute method on Odoo model.

        Args:
            model: Model name (e.g., 'account.move')
            method: Method name (e.g., 'search_read')
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Result of the method call
        """
        self._ensure_connected()

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        try:
            models = xmlrpc.client.ServerProxy(self.object_endpoint)
            return models.execute_kw(
                self.database, self.uid, self.password, model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f"Error executing {method} on {model}: {e}")
            raise

    # === Accounting Methods ===

    def get_invoices(
        self,
        state: Optional[str] = None,
        move_type: str = "out_invoice",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get customer invoices from Odoo.

        Args:
            state: Filter by state ('draft', 'posted', 'cancel')
            move_type: 'out_invoice' for customer, 'in_invoice' for vendor
            date_from: Filter from date
            date_to: Filter to date
            limit: Max results

        Returns:
            List of invoice dictionaries
        """
        domain = [("move_type", "=", move_type)]

        if state:
            domain.append(("state", "=", state))

        if date_from:
            domain.append(("invoice_date", ">=", date_from))

        if date_to:
            domain.append(("invoice_date", "<=", date_to))

        fields = [
            "id",
            "name",
            "amount_total",
            "amount_residual",
            "invoice_date",
            "invoice_date_due",
            "state",
            "payment_state",
            "partner_id",
            "currency_id",
            "move_type",
        ]

        result = self.execute_kw(
            "account.move", "search_read", [domain], {"fields": fields, "limit": limit, "order": "invoice_date desc"}
        )

        return self._format_invoices(result)

    def get_vendor_bills(
        self,
        state: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get vendor bills from Odoo.

        Args:
            state: Filter by state
            date_from: Filter from date
            date_to: Filter to date
            limit: Max results

        Returns:
            List of vendor bill dictionaries
        """
        return self.get_invoices(
            state=state, move_type="in_invoice", date_from=date_from, date_to=date_to, limit=limit
        )

    def get_payments(
        self,
        payment_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get payments from Odoo.

        Args:
            payment_type: 'inbound' or 'outbound'
            date_from: Filter from date
            date_to: Filter to date
            limit: Max results

        Returns:
            List of payment dictionaries
        """
        domain = []

        if payment_type:
            domain.append(("payment_type", "=", payment_type))

        if date_from:
            domain.append(("date", ">=", date_from))

        if date_to:
            domain.append(("date", "<=", date_to))

        fields = [
            "id",
            "name",
            "amount",
            "date",
            "state",
            "payment_type",
            "partner_id",
            "journal_id",
            "currency_id",
            "payment_method_id",
        ]

        result = self.execute_kw(
            "account.payment", "search_read", [domain], {"fields": fields, "limit": limit, "order": "date desc"}
        )

        return self._format_payments(result)

    def get_revenue(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> float:
        """
        Calculate total revenue from posted customer invoices.

        Args:
            date_from: Filter from date
            date_to: Filter to date

        Returns:
            Total revenue amount
        """
        domain = [("move_type", "=", "out_invoice"), ("state", "=", "posted")]

        if date_from:
            domain.append(("invoice_date", ">=", date_from))
        if date_to:
            domain.append(("invoice_date", "<=", date_to))

        invoices = self.execute_kw("account.move", "search_read", [domain], {"fields": ["amount_total"]})

        total = sum(inv.get("amount_total", 0) for inv in invoices)
        return total

    def get_expenses(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> float:
        """
        Calculate total expenses from posted vendor bills.

        Args:
            date_from: Filter from date
            date_to: Filter to date

        Returns:
            Total expense amount
        """
        domain = [("move_type", "=", "in_invoice"), ("state", "=", "posted")]

        if date_from:
            domain.append(("invoice_date", ">=", date_from))
        if date_to:
            domain.append(("invoice_date", "<=", date_to))

        bills = self.execute_kw("account.move", "search_read", [domain], {"fields": ["amount_total"]})

        total = sum(bill.get("amount_total", 0) for bill in bills)
        return total

    def get_overdue_invoices(self, days_overdue: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get overdue customer invoices.

        Args:
            days_overdue: Minimum days overdue
            limit: Max results

        Returns:
            List of overdue invoices
        """
        # Get current date
        today = datetime.now().strftime("%Y-%m-%d")

        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "!=", "paid"),
            ("invoice_date_due", "<", today),
        ]

        fields = [
            "id",
            "name",
            "amount_total",
            "amount_residual",
            "invoice_date",
            "invoice_date_due",
            "partner_id",
            "payment_state",
        ]

        result = self.execute_kw(
            "account.move", "search_read", [domain], {"fields": fields, "limit": limit, "order": "invoice_date_due asc"}
        )

        invoices = self._format_invoices(result)

        # Filter by days overdue
        if days_overdue > 0:
            cutoff = datetime.now() - timedelta(days=days_overdue)
            invoices = [
                inv
                for inv in invoices
                if inv.get("due_date") and datetime.strptime(inv["due_date"], "%Y-%m-%d") < cutoff
            ]

        return invoices

    def get_account_balance(self, account_code: Optional[str] = None) -> float:
        """
        Get account balance.

        Args:
            account_code: Account code filter (e.g., '1100' for Cash)

        Returns:
            Account balance
        """
        try:
            # Search for account by code
            domain = [('code', '=', account_code)] if account_code else []
            accounts = self.execute('account.account', 'search_read', {
                'domain': domain,
                'fields': ['id', 'name', 'code', 'current_balance', 'company_id'],
                'limit': 1
            })

            if not accounts:
                # If no specific account found, try to get a default asset account
                default_domain = [
                    ('user_type', '=', 'regular'),
                    ('company_id', '=', self.company_id)
                ]
                accounts = self.execute('account.account', 'search_read', {
                    'domain': default_domain,
                    'fields': ['id', 'name', 'code', 'current_balance'],
                    'order': 'code ASC',
                    'limit': 1
                })

            if accounts:
                balance = accounts[0].get('current_balance', 0.0)
                self.logger.debug(f"Account balance for {accounts[0]['name']}: {balance}")
                return float(balance)
            else:
                self.logger.warning("No accounts found for balance query")
                return 0.0

        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            return 0.0

    def _format_invoices(self, invoices: List[Dict]) -> List[Dict[str, Any]]:
        """Format invoice data for easier consumption."""
        formatted = []

        for inv in invoices:
            partner = inv.get("partner_id")
            currency = inv.get("currency_id")

            formatted_inv = {
                "id": inv["id"],
                "name": inv["name"],
                "amount_total": inv.get("amount_total", 0.0),
                "amount_residual": inv.get("amount_residual", 0.0),
                "date": inv.get("invoice_date", ""),
                "due_date": inv.get("invoice_date_due", ""),
                "state": inv.get("state", ""),
                "payment_state": inv.get("payment_state", ""),
                "partner_id": partner[0] if partner else None,
                "partner_name": partner[1] if partner else "Unknown",
                "currency": currency[1] if currency else "USD",
                "move_type": inv.get("move_type", ""),
                "type": "invoice" if inv.get("move_type") == "out_invoice" else "vendor_bill",
            }

            formatted.append(formatted_inv)

        return formatted

    def _format_payments(self, payments: List[Dict]) -> List[Dict[str, Any]]:
        """Format payment data for easier consumption."""
        formatted = []

        for pay in payments:
            partner = pay.get("partner_id")
            journal = pay.get("journal_id")

            formatted_pay = {
                "id": pay["id"],
                "name": pay["name"],
                "amount": pay.get("amount", 0.0),
                "date": pay.get("date", ""),
                "state": pay.get("state", ""),
                "payment_type": pay.get("payment_type", ""),
                "partner_id": partner[0] if partner else None,
                "partner_name": partner[1] if partner else "Unknown",
                "journal_id": journal[0] if journal else None,
                "journal_name": journal[1] if journal else "Unknown",
                "type": "payment",
            }

            formatted.append(formatted_pay)

        return formatted


class AuthenticationError(Exception):
    """Odoo authentication failed."""
    pass


class ConnectionError(Exception):
    """Odoo connection failed."""
    pass


# Test connection
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    client = OdooClient()

    try:
        client.connect()
        print("✅ Connected to Odoo successfully")

        # Test query
        invoices = client.get_invoices(limit=5)
        print(f"✅ Found {len(invoices)} invoices")

        payments = client.get_payments(limit=5)
        print(f"✅ Found {len(payments)} payments")

    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("\nTip: Make sure Odoo is running at http://localhost:8069")
        print("     Run: cd docker/odoo && START_ODOO.bat")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
