#!/usr/bin/env python3
"""
Create test data in Odoo - Customer and Invoice
"""

from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Connect to existing Chrome CDP
        browser = p.chromium.connect("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Odoo...")
        page.goto("http://localhost:8069", timeout=30000)
        page.wait_for_timeout(3000)

        # Click on Invoicing app
        print("Opening Invoicing app...")
        try:
            page.click("text=Invoicing", timeout=10000)
            page.wait_for_timeout(2000)

            # Create Customer first
            print("Creating test customer...")
            page.click("text=Customers", timeout=10000)
            page.wait_for_timeout(2000)
            page.click("button:has-text('Create')", timeout=10000)
            page.wait_for_timeout(2000)

            # Fill customer form
            page.fill('input[name="name"]', 'Test Customer')
            page.fill('input[name="email"]', 'test@example.com')
            page.press('input[name="name"]', 'Enter')
            page.wait_for_timeout(3000)

            print("Customer created successfully!")

            # Now create invoice
            print("Creating test invoice...")
            page.goto("http://localhost:8069/web#view_type=list&model=account.move&action=355", timeout=30000)
            page.wait_for_timeout(3000)

            page.click("button:has-text('Create')", timeout=10000)
            page.wait_for_timeout(2000)

            # Select customer
            page.click('.o_field_many2one[name="partner_id"] input', timeout=10000)
            page.wait_for_timeout(1000)
            page.keyboard.type('Test Customer')
            page.wait_for_timeout(2000)
            page.keyboard.press('Enter')
            page.wait_for_timeout(2000)

            # Add invoice line
            page.click('.o_field_x2many_list_row_add a:has-text("Add a line")', timeout=10000)
            page.wait_for_timeout(2000)

            # Fill product/service
            page.fill('.o_field_widget[name="product_id"] input', 'Service')
            page.wait_for_timeout(1000)
            page.keyboard.press('Enter')
            page.wait_for_timeout(2000)

            # Set quantity and price
            page.fill('input[name="quantity"]', '1')
            page.fill('input[name="price_unit"]', '1000')
            page.wait_for_timeout(1000)

            # Save
            page.click("button:has-text('Save')", timeout=10000)
            page.wait_for_timeout(3000)

            # Confirm the invoice
            page.click("button:has-text('Confirm')", timeout=10000)
            page.wait_for_timeout(3000)

            print("Invoice created and confirmed successfully!")
            print("Test data creation complete!")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="odoo_debug.png")
            print("Screenshot saved to odoo_debug.png")

        browser.close()

if __name__ == "__main__":
    main()
