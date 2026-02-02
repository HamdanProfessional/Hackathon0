#!/usr/bin/env python3
"""
Send Test Email - Direct Gmail API
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_servers.email_mcp.src.email_client import EmailClient

# Initialize email client
client = EmailClient(
    credentialsPath="mcp-servers/email-mcp",
    tokenPath="mcp-servers/email-mcp/.gmail_mcp_token.json"
)

# Send test email
print("Sending test email to n00bi2761@gmail.com...")

result = client.send_email(
    to="n00bi2761@gmail.com",
    subject="Test Email from AI Employee System",
    body="""Hi,

This is a test email from the AI Employee system!

Best regards,
AI Employee"""
)

if result.get("success"):
    print("✅ Email sent successfully!")
    print(f"Message ID: {result.get('message_id')}")
else:
    print(f"❌ Failed to send email: {result.get('error')}")
    sys.exit(1)
