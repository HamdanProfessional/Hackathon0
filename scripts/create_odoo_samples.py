#!/usr/bin/env python3
"""
Create Sample Data for Odoo Testing

Creates sample invoices, payments, and vendor bills in Odoo for testing.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient

# Odoo connection details
ODOO_URL = "http://143.244.143.143:8069"
ODOO_DB = "odoo"
ODOO_USER = "admin"
ODOO_PASSWORD = "admin"

def create_sample_data():
    """Create sample data in Odoo."""
    print("[INFO] Connecting to Odoo...")

    # Create Odoo client
    client = OdooClient(
        url=ODOO_URL,
        database=ODOO_DB,
        username=ODOO_USER,
        password=ODOO_PASSWORD
    )

    # Connect
    uid = client.connect()
    print(f"[INFO] Connected as {ODOO_USER} (uid: {uid})")

    # Create a sample customer
    print("[INFO] Creating sample customer...")
    customer_id = client.execute_kw('res.partner', 'create', [{
        'name': 'Test Client Inc.',
        'email': 'test@clientinc.com',
        'is_company': True,
        'customer_rank': 1,
    }])
    print(f"[INFO] Created customer ID: {customer_id}")

    # Create a sample invoice
    print("[INFO] Creating sample customer invoice...")
    today = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    # First, we need to get a valid product/account for the invoice line
    # Search for an existing revenue account
    accounts = client.execute_kw('account.account', 'search_read', [
        [('account_type', '=', 'asset_receivable')]
    ], {'fields': ['id', 'name'], 'limit': 1})

    receivable_account_id = accounts[0]['id'] if accounts else None

    # Search for an existing revenue account for the product
    revenue_accounts = client.execute_kw('account.account', 'search_read', [
        [('account_type', '=', 'income')]
    ], {'fields': ['id', 'name'], 'limit': 1})

    revenue_account_id = revenue_accounts[0]['id'] if revenue_accounts else None

    if not receivable_account_id or not revenue_account_id:
        print("[ERROR] Could not find required accounts. Please ensure accounting is fully initialized.")
        return

    # Create invoice with proper line structure
    invoice_data = {
        'move_type': 'out_invoice',
        'partner_id': customer_id,
        'invoice_date': today,
        'date': today,
        'ref': 'INV-2026-001',
        'invoice_line_ids': [
            (0, 0, {
                'name': 'Consulting Services',
                'quantity': 10.0,
                'price_unit': 150.00,
                'account_id': revenue_account_id,
            })
        ],
    }

    invoice_id = client.execute_kw('account.move', 'create', [invoice_data])
    print(f"[INFO] Created invoice ID: {invoice_id}")

    # Confirm the invoice (move to posted state)
    client.execute_kw('account.move', 'action_post', [[invoice_id]])
    print(f"[INFO] Posted invoice: INV-2026-001")

    # Create a sample vendor
    print("[INFO] Creating sample vendor...")
    vendor_id = client.execute_kw('res.partner', 'create', [{
        'name': 'Office Supplies Co.',
        'supplier_rank': 1,
        'is_company': True,
    }])
    print(f"[INFO] Created vendor ID: {vendor_id}")

    # Search for payable account
    payable_accounts = client.execute_kw('account.account', 'search_read', [
        [('account_type', '=', 'liability_payable')]
    ], {'fields': ['id', 'name'], 'limit': 1})

    payable_account_id = payable_accounts[0]['id'] if payable_accounts else None

    # Search for expense account
    expense_accounts = client.execute_kw('account.account', 'search_read', [
        [('account_type', '=', 'expense')]
    ], {'fields': ['id', 'name'], 'limit': 1})

    expense_account_id = expense_accounts[0]['id'] if expense_accounts else None

    if not payable_account_id or not expense_account_id:
        print("[ERROR] Could not find required accounts for vendor bill.")
        return

    # Create vendor bill
    bill_data = {
        'move_type': 'in_invoice',
        'partner_id': vendor_id,
        'invoice_date': today,
        'date': today,
        'ref': 'BILL-2026-001',
        'invoice_line_ids': [
            (0, 0, {
                'name': 'Office Supplies',
                'quantity': 5.0,
                'price_unit': 45.00,
                'account_id': expense_account_id,
            })
        ],
    }

    bill_id = client.execute_kw('account.move', 'create', [bill_data])
    print(f"[INFO] Created vendor bill ID: {bill_id}")

    # Confirm the bill
    client.execute_kw('account.move', 'action_post', [[bill_id]])
    print(f"[INFO] Posted bill: BILL-2026-001")

    # Create a sample payment
    print("[INFO] Creating sample payment...")

    # Find a payment journal (usually Bank or Cash)
    journals = client.execute_kw('account.journal', 'search_read', [
        [('type', 'in', ['bank', 'cash'])]
    ], {'fields': ['id', 'name', 'type'], 'limit': 1})

    if not journals:
        print("[ERROR] Could not find a payment journal (Bank/Cash).")
        return

    journal_id = journals[0]['id']
    journal_name = journals[0]['name']
    print(f"[INFO] Using journal: {journal_name} (ID: {journal_id})")

    payment_data = {
        'payment_type': 'inbound',
        'partner_id': customer_id,
        'amount': 500.00,
        'date': today,
        'memo': 'PAY-2026-001',
        'journal_id': journal_id,
        'payment_method_id': 1,  # Default payment method
    }

    payment_id = client.execute_kw('account.payment', 'create', [payment_data])
    print(f"[INFO] Created payment ID: {payment_id}")

    # Post the payment (using post method for payments)
    try:
        client.execute_kw('account.payment', 'post', [[payment_id]])
        print(f"[INFO] Posted payment: PAY-2026-001")
    except Exception as e:
        print(f"[WARNING] Could not post payment (may already be posted): {e}")
        # Try to validate it instead
        try:
            client.execute_kw('account.payment', 'action_validate', [[payment_id]])
            print(f"[INFO] Validated payment: PAY-2026-001")
        except Exception as e2:
            print(f"[INFO] Payment created but may need manual posting: {e2}")

    print("\n[SUCCESS] Sample data created:")
    print(f"  Customer: Test Client Inc. (ID: {customer_id})")
    print(f"  Invoice: INV-2026-001 - $1,500.00 (ID: {invoice_id})")
    print(f"  Vendor Bill: BILL-2026-001 - $225.00 (ID: {bill_id})")
    print(f"  Payment: PAY-2026-001 - $500.00 (ID: {payment_id})")

if __name__ == "__main__":
    create_sample_data()
