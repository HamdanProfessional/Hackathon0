#!/usr/bin/env python3
"""
Domain Classifier for AI Employee

Classifies tasks and events into Personal or Business domains for cross-domain coordination.

Usage:
    from watchers.domain_classifier import Domain, classify_domain

    domain = classify_domain("invoice", "client@example.com")
    # Returns: Domain.BUSINESS

    domain = classify_domain("doctor appointment", "health clinic")
    # Returns: Domain.PERSONAL
"""

from enum import Enum
from typing import Optional, List
import re


class Domain(Enum):
    """Domain categories for cross-domain coordination."""
    PERSONAL = "personal"
    BUSINESS = "business"
    SHARED = "shared"  # Items that apply to both domains


# Business-related keywords and patterns
BUSINESS_KEYWORDS = [
    "invoice", "payment", "client", "customer", "contract", "proposal",
    "meeting", "conference", "webinar", "presentation", "report",
    "project", "deadline", "deliverable", "milestone", "scope",
    "social media", "post", "content", "marketing", "campaign",
    "accounting", "expense", "budget", "revenue", "profit",
    "vendor", "supplier", "partner", "stakeholder", "investor",
    "hr", "hiring", "recruitment", "payroll", "employee",
    "sales", "lead", "opportunity", "deal", "pipeline",
    "support", "ticket", "issue", "resolution", "sla"
]

# Business-related email domains (common company email patterns)
BUSINESS_EMAIL_PATTERNS = [
    r"@.*\.com$",  # Company emails (generic)
    r"@.*\..*\.com$",  # Subdomain companies
    r"@.*\.biz$",  # Business TLD
    r"@.*\.org$",  # Organization TLD
]

# Personal-related keywords
PERSONAL_KEYWORDS = [
    "doctor", "dentist", "medical", "health", "appointment", "pharmacy",
    "family", "personal", "friend", "birthday", "anniversary",
    "shopping", "grocery", "personal purchase", "home", "rent",
    "utility", "electricity", "water", "internet", "phone",
    "insurance", "personal insurance", "car insurance", "home insurance",
    "bank", "personal banking", "credit card", "loan", "mortgage",
    "school", "education", "course", "training", "certification",
    "vacation", "holiday", "travel", "personal trip",
    "gym", "fitness", "hobby", "personal interest"
]

# Shared-domain keywords (apply to both Personal and Business)
SHARED_KEYWORDS = [
    "urgent", "asap", "important", "priority",
    "reminder", "follow up", "check", "review",
    "schedule", "calendar", "availability",
    "document", "file", "attachment"
]

# Sender email patterns for known services
PERSONAL_SENDER_PATTERNS = [
    r"@gmail\.com$",
    r"@yahoo\.com$",
    r"@outlook\.com$",
    r"@hotmail\.com$",
    r"@icloud\.com$",
    r"@protonmail\.com$",
]


def classify_domain(
    subject: str = "",
    content: str = "",
    sender: str = "",
    source: str = ""
) -> Domain:
    """
    Classify an item into Personal, Business, or Shared domain.

    Args:
        subject: Subject line or title
        content: Body content or description
        sender: Sender email address or name
        source: Source system (e.g., "gmail", "slack", "whatsapp")

    Returns:
        Domain enum value (PERSONAL, BUSINESS, or SHARED)
    """
    # Combine all text for analysis
    combined_text = f"{subject} {content} {sender}".lower()

    # Check for shared keywords first (highest priority)
    for keyword in SHARED_KEYWORDS:
        if keyword in combined_text:
            return Domain.SHARED

    # Check business keywords
    business_score = 0
    for keyword in BUSINESS_KEYWORDS:
        if keyword in combined_text:
            business_score += 1

    # Check personal keywords
    personal_score = 0
    for keyword in PERSONAL_KEYWORDS:
        if keyword in combined_text:
            personal_score += 1

    # Check sender email domain
    if sender:
        sender_lower = sender.lower()
        # Check personal email patterns
        for pattern in PERSONAL_SENDER_PATTERNS:
            if re.search(pattern, sender_lower):
                personal_score += 2  # Weight personal email patterns higher

        # Check business email patterns
        for pattern in BUSINESS_EMAIL_PATTERNS:
            if re.search(pattern, sender_lower):
                # Exclude common personal domains from business patterns
                if not re.search(r"@gmail|@yahoo|@outlook|@hotmail|@icloud", sender_lower):
                    business_score += 2

    # Source-based classification
    source_lower = source.lower()
    if source_lower in ["xero", "odoo", "linkedin", "twitter", "facebook", "instagram"]:
        business_score += 3
    elif source_lower in ["personal", "family"]:
        personal_score += 3

    # Determine domain based on scores
    if business_score > personal_score:
        return Domain.BUSINESS
    elif personal_score > business_score:
        return Domain.PERSONAL
    else:
        # If scores are equal or both zero, check for more specific indicators
        if "client" in combined_text or "invoice" in combined_text or "payment" in combined_text:
            return Domain.BUSINESS
        elif "family" in combined_text or "personal" in combined_text:
            return Domain.PERSONAL
        else:
            # Default to BUSINESS for work-related sources, PERSONAL for ambiguous
            return Domain.BUSINESS if source_lower in ["gmail", "calendar", "slack"] else Domain.SHARED


def get_domain_folder(vault_path: str, domain: Domain) -> str:
    """
    Get the folder path for a specific domain.

    Args:
        vault_path: Path to the vault
        domain: Domain enum value

    Returns:
        Path to domain-specific folder
    """
    from pathlib import Path

    vault = Path(vault_path)

    if domain == Domain.PERSONAL:
        return str(vault / "Needs_Action" / "Personal")
    elif domain == Domain.BUSINESS:
        return str(vault / "Needs_Action" / "Business")
    else:  # SHARED
        return str(vault / "Needs_Action" / "Shared")


def ensure_domain_folders(vault_path: str):
    """
    Ensure domain-specific folders exist in the vault.

    Args:
        vault_path: Path to the vault
    """
    from pathlib import Path

    vault = Path(vault_path)
    needs_action = vault / "Needs_Action"

    for domain in Domain:
        domain_folder = needs_action / domain.value.capitalize()
        domain_folder.mkdir(parents=True, exist_ok=True)


def classify_and_route(
    filepath: str,
    vault_path: str,
    subject: str = "",
    content: str = "",
    sender: str = "",
    source: str = ""
) -> tuple:
    """
    Classify a file and move it to the appropriate domain folder.

    Args:
        filepath: Path to the file to route
        vault_path: Path to the vault
        subject: Subject line or title
        content: Body content or description
        sender: Sender email address or name
        source: Source system

    Returns:
        Tuple of (domain, new_filepath)
    """
    from pathlib import Path

    # Classify the domain
    domain = classify_domain(subject, content, sender, source)

    # Get target folder
    target_folder = get_domain_folder(vault_path, domain)

    # Ensure folder exists
    Path(target_folder).mkdir(parents=True, exist_ok=True)

    # Move file
    source_path = Path(filepath)
    target_path = Path(target_folder) / source_path.name

    import shutil
    shutil.move(str(source_path), str(target_path))

    return domain, str(target_path)


# CLI for testing
if __name__ == "__main__":
    import sys

    print("Domain Classifier Test")
    print("=" * 60)

    test_cases = [
        {
            "subject": "Invoice #1234 from Acme Corp",
            "content": "Please find attached invoice for services rendered",
            "sender": "billing@acmecorp.com",
            "source": "gmail"
        },
        {
            "subject": "Doctor Appointment Tomorrow",
            "content": "Reminder: Your appointment with Dr. Smith at 10 AM",
            "sender": "clinic@healthcare.com",
            "source": "gmail"
        },
        {
            "subject": "Urgent: Project Deadline",
            "content": "The deadline is approaching, please review",
            "sender": "manager@company.com",
            "source": "slack"
        },
        {
            "subject": "Birthday Party Invitation",
            "content": "You're invited to celebrate!",
            "sender": "friend@gmail.com",
            "source": "gmail"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        domain = classify_domain(
            test["subject"],
            test["content"],
            test["sender"],
            test["source"]
        )
        print(f"\nTest {i}: {test['subject'][:50]}...")
        print(f"  Domain: {domain.value.upper()}")
        print(f"  From: {test['sender']}")

    print("\n" + "=" * 60)
