#!/usr/bin/env python3
"""
Audit Logic - Transaction Analysis for Business Insights

Analyzes financial transactions to detect subscriptions, recurring expenses,
and other patterns for the CEO briefing.

This is the implementation shown in Hackathon0.md (line 507).

Usage:
    from utils.audit_logic import analyze_transaction, get_subscription_patterns

    # Check if a transaction is a subscription
    result = analyze_transaction({
        'description': 'Netflix Subscription',
        'amount': 15.99,
        'date': '2026-01-15'
    })

    if result:
        print(f"Subscription detected: {result['name']} - ${result['amount']}")
"""

from typing import Dict, Optional, List


# ==================== SUBSCRIPTION DETECTION ====================

SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'amazon prime': 'Amazon Prime',
    'amazon web services': 'AWS',
    'google cloud': 'Google Cloud',
    'microsoft 365': 'Microsoft 365',
    'office 365': 'Microsoft 365',
    'dropbox': 'Dropbox',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'zoom': 'Zoom',
    'atlassian': 'Atlassian',
    'jira': 'Jira',
    'confluence': 'Confluence',
    'salesforce': 'Salesforce',
    'hubspot': 'HubSpot',
    'mailchimp': 'Mailchimp',
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'chatgpt': 'ChatGPT',
    'claude': 'Claude AI',
    'fiverr': 'Fiverr',
    'upwork': 'Upwork',
    'aws': 'Amazon Web Services',
    'gcp': 'Google Cloud Platform',
    'azure': 'Microsoft Azure',
    'digitalocean': 'DigitalOcean',
    'heroku': 'Heroku',
    'vercel': 'Vercel',
    'netlify': 'Netlify',
    'shopify': 'Shopify',
    'squarespace': 'Squarespace',
    'wordpress': 'WordPress',
    'hostinger': 'Hostinger',
    'godaddy': 'GoDaddy',
    'namecheap': 'Namecheap',
    'nordvpn': 'NordVPN',
    'expressvpn': 'ExpressVPN',
    'surfshark': 'Surfshark',
    '1password': '1Password',
    'lastpass': 'LastPass',
    'bitwarden': 'Bitwarden',
    'carbonite': 'Carbonite',
    'backblaze': 'Backblaze',
}


def get_subscription_patterns() -> Dict[str, str]:
    """
    Get the subscription pattern dictionary.

    Returns:
        Dictionary of patterns to service names
    """
    return SUBSCRIPTION_PATTERNS.copy()


def add_subscription_pattern(pattern: str, name: str):
    """
    Add or update a subscription pattern.

    Args:
        pattern: Search pattern (e.g., 'service.com')
        name: Display name (e.g., 'Service Name')
    """
    SUBSCRIPTION_PATTERNS[pattern.lower()] = name


def analyze_transaction(transaction: Dict) -> Optional[Dict]:
    """
    Analyze a transaction to detect if it's a subscription.

    Args:
        transaction: Dictionary with keys:
            - description: Transaction description (string)
            - amount: Transaction amount (float)
            - date: Transaction date (string or datetime)

    Returns:
        Dictionary with subscription info if found, None otherwise:
        {
            'type': 'subscription',
            'name': 'Service Name',
            'amount': 15.99,
            'date': '2026-01-15'
        }
    """
    description = transaction.get('description', '').lower()

    for pattern, name in SUBSCRIPTION_PATTERNS.items():
        if pattern in description:
            return {
                'type': 'subscription',
                'name': name,
                'amount': transaction.get('amount', 0),
                'date': transaction.get('date'),
                'description': transaction.get('description')
            }

    return None


# ==================== EXPENSE CATEGORIZATION ====================

EXPENSE_CATEGORIES = {
    'software': ['software', 'saas', 'subscription', 'app', 'service'],
    'hardware': ['computer', 'laptop', 'monitor', 'phone', 'device', 'hardware'],
    'office': ['office', 'furniture', 'supplies', 'desk', 'chair'],
    'marketing': ['ads', 'facebook', 'google ads', 'marketing', 'promotion'],
    'travel': ['flight', 'hotel', 'uber', 'lyft', 'travel', 'airbnb'],
    'food': ['restaurant', 'coffee', 'food', 'meal', 'lunch', 'dinner'],
    'utilities': ['electricity', 'water', 'gas', 'internet', 'phone bill'],
    'insurance': ['insurance', 'liability', 'coverage'],
    'legal': ['legal', 'attorney', 'lawyer', 'contract'],
    'freelance': ['fiverr', 'upwork', 'freelancer', 'contractor'],
}


def categorize_transaction(transaction: Dict) -> Optional[str]:
    """
    Categorize a transaction based on its description.

    Args:
        transaction: Dictionary with 'description' key

    Returns:
        Category name or None if uncategorized
    """
    description = transaction.get('description', '').lower()

    for category, keywords in EXPENSE_CATEGORIES.items():
        if any(keyword in description for keyword in keywords):
            return category

    return 'other'


# ==================== ANOMALY DETECTION ====================

def detect_unusual_expense(
    transaction: Dict,
    avg_amount: float,
    threshold_multiplier: float = 2.0
) -> Optional[Dict]:
    """
    Detect if a transaction amount is unusual compared to average.

    Args:
        transaction: Dictionary with 'amount' key
        avg_amount: Average transaction amount for comparison
        threshold_multiplier: How many times the average triggers alert (default: 2.0x)

    Returns:
        Anomaly info dictionary or None
    """
    amount = transaction.get('amount', 0)

    if amount > (avg_amount * threshold_multiplier):
        return {
            'type': 'unusual_expense',
            'amount': amount,
            'average': avg_amount,
            'multiplier': amount / avg_amount,
            'description': transaction.get('description')
        }

    return None


def detect_large_transaction(
    transaction: Dict,
    threshold: float = 500.0
) -> Optional[Dict]:
    """
    Detect if a transaction exceeds a threshold amount.

    Args:
        transaction: Dictionary with 'amount' key
        threshold: Amount threshold (default: $500)

    Returns:
        Alert info dictionary or None
    """
    amount = transaction.get('amount', 0)

    if amount >= threshold:
        return {
            'type': 'large_transaction',
            'amount': amount,
            'threshold': threshold,
            'description': transaction.get('description'),
            'date': transaction.get('date')
        }

    return None


# ==================== BATCH ANALYSIS ====================

def analyze_transactions(transactions: List[Dict]) -> Dict:
    """
    Analyze a batch of transactions and generate insights.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Analysis results dictionary:
        {
            'total': 100,
            'subscriptions': [...],
            'by_category': {'software': 500, 'hardware': 2000},
            'unusual': [...],
            'large_transactions': [...]
        }
    """
    results = {
        'total': len(transactions),
        'subscriptions': [],
        'by_category': {},
        'unusual': [],
        'large_transactions': [],
        'total_amount': 0
    }

    # Calculate total amount for average
    total_amount = sum(t.get('amount', 0) for t in transactions)
    avg_amount = total_amount / len(transactions) if transactions else 0
    results['total_amount'] = total_amount
    results['average_amount'] = avg_amount

    for transaction in transactions:
        # Check for subscriptions
        sub = analyze_transaction(transaction)
        if sub:
            results['subscriptions'].append(sub)

        # Categorize
        category = categorize_transaction(transaction)
        results['by_category'][category] = results['by_category'].get(category, 0) + transaction.get('amount', 0)

        # Check for unusual expenses
        unusual = detect_unusual_expense(transaction, avg_amount)
        if unusual:
            results['unusual'].append(unusual)

        # Check for large transactions
        large = detect_large_transaction(transaction)
        if large:
            results['large_transactions'].append(large)

    return results


# ==================== EXAMPLES ====================

if __name__ == "__main__":
    print("="*60)
    print("AUDIT LOGIC - TRANSACTION ANALYSIS")
    print("="*60)

    # Example transactions
    sample_transactions = [
        {'description': 'Netflix Subscription', 'amount': 15.99, 'date': '2026-01-15'},
        {'description': 'Adobe Creative Cloud', 'amount': 54.99, 'date': '2026-01-14'},
        {'description': 'AWS Usage', 'amount': 23.45, 'date': '2026-01-13'},
        {'description': 'Office Supplies Store', 'amount': 125.00, 'date': '2026-01-12'},
        {'description': 'Client Payment', 'amount': 2500.00, 'date': '2026-01-11'},
        {'description': 'Software Purchase', 'amount': 499.99, 'date': '2026-01-10'},
    ]

    print("\n1. Subscription Detection:")
    print("-"*40)

    for txn in sample_transactions:
        result = analyze_transaction(txn)
        if result:
            print(f"   ✓ {result['name']}: ${result['amount']:.2f}")
        else:
            print(f"   - {txn['description']}: Not a subscription")

    print("\n2. Categorization:")
    print("-"*40)

    for txn in sample_transactions:
        category = categorize_transaction(txn)
        print(f"   {txn['description']}: {category}")

    print("\n3. Large Transaction Detection (>$500):")
    print("-"*40)

    for txn in sample_transactions:
        large = detect_large_transaction(txn, threshold=500)
        if large:
            print(f"   ⚠️  {large['description']}: ${large['amount']:.2f}")

    print("\n4. Full Analysis:")
    print("-"*40)

    analysis = analyze_transactions(sample_transactions)

    print(f"   Total transactions: {analysis['total']}")
    print(f"   Total amount: ${analysis['total_amount']:.2f}")
    print(f"   Average: ${analysis['average_amount']:.2f}")
    print(f"\n   Subscriptions found: {len(analysis['subscriptions'])}")
    for sub in analysis['subscriptions']:
        print(f"      - {sub['name']}: ${sub['amount']:.2f}")

    print(f"\n   Spending by category:")
    for category, amount in analysis['by_category'].items():
        print(f"      - {category}: ${amount:.2f}")

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)
