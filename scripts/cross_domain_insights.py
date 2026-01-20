#!/usr/bin/env python3
"""
Cross-Domain Insights Script

Generates unified insights across Personal and Business domains.
Provides cross-domain coordination, conflict detection, and recommendations.

Usage:
    python scripts/cross_domain_insights.py --vault AI_Employee_Vault
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.domain_classifier import Domain, classify_domain


class CrossDomainAnalyzer:
    """Analyzes items across Personal and Business domains."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.plans = self.vault_path / "Plans"
        self.logs = self.vault_path / "Logs"

    def scan_domain_folders(self) -> Dict[str, List[Dict]]:
        """Scan all domain folders and categorize items."""
        domains = {
            Domain.PERSONAL: [],
            Domain.BUSINESS: [],
            Domain.SHARED: []
        }

        # Also scan flat Needs_Action for items not yet classified
        flat_items = []

        # Scan domain-specific folders
        for domain in Domain:
            domain_folder = self.needs_action / domain.value.capitalize()
            if domain_folder.exists():
                for item_file in domain_folder.glob("*.md"):
                    item = self._parse_item_file(item_file, domain)
                    if item:
                        domains[domain].append(item)

        # Scan flat Needs_Action for unclassified items
        if self.needs_action.exists():
            for item_file in self.needs_action.glob("*.md"):
                # Skip domain subfolders
                if item_file.parent.name in [d.value.capitalize() for d in Domain]:
                    continue
                item = self._parse_item_file(item_file, None)
                if item:
                    flat_items.append(item)

        return domains, flat_items

    def _parse_item_file(self, filepath: Path, domain: Domain = None) -> Dict:
        """Parse an item file and extract metadata."""
        try:
            content = filepath.read_text(encoding='utf-8')

            # Extract frontmatter
            frontmatter = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    for line in parts[1].split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip()

            item_type = frontmatter.get('type', 'unknown')
            source = frontmatter.get('source', 'unknown')
            subject = frontmatter.get('subject', '')
            priority = frontmatter.get('priority', 'normal')

            # Auto-classify if domain not provided
            if domain is None:
                sender = frontmatter.get('from', '')
                domain = classify_domain(
                    subject=subject,
                    content=content[:500],
                    sender=sender,
                    source=source
                )

            return {
                'filepath': filepath,
                'filename': filepath.name,
                'type': item_type,
                'source': source,
                'subject': subject,
                'domain': domain,
                'priority': priority,
                'frontmatter': frontmatter,
                'content': content
            }
        except Exception as e:
            print(f"Warning: Could not parse {filepath.name}: {e}")
            return None

    def detect_conflicts(self, domains: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect cross-domain conflicts."""
        conflicts = []

        # Time-based conflicts (if items have date/time)
        personal_by_time = {}
        business_by_time = {}

        for item in domains.get(Domain.PERSONAL, []):
            date_str = item['frontmatter'].get('date') or item['frontmatter'].get('time')
            if date_str:
                personal_by_time[date_str] = item

        for item in domains.get(Domain.BUSINESS, []):
            date_str = item['frontmatter'].get('date') or item['frontmatter'].get('time')
            if date_str and date_str in personal_by_time:
                conflicts.append({
                    'type': 'time_conflict',
                    'personal': personal_by_time[date_str],
                    'business': item,
                    'time': date_str
                })

        # Priority-based conflicts
        high_priority_personal = [i for i in domains.get(Domain.PERSONAL, [])
                                   if i['priority'].startswith('!!!')]
        high_priority_business = [i for i in domains.get(Domain.BUSINESS, [])
                                  if i['priority'].startswith('!!!')]

        if len(high_priority_personal) > 3 and len(high_priority_business) > 3:
            conflicts.append({
                'type': 'overload_warning',
                'message': f"Too many high-priority items: {len(high_priority_personal)} personal, {len(high_priority_business)} business",
                'personal_count': len(high_priority_personal),
                'business_count': len(high_priority_business)
            })

        return conflicts

    def generate_insights(self) -> Dict[str, Any]:
        """Generate cross-domain insights."""
        domains, flat_items = self.scan_domain_folders()

        # Count items by domain and type
        domain_counts = {}
        domain_type_counts = {d: defaultdict(int) for d in Domain}

        for domain, items in domains.items():
            domain_counts[domain.value] = len(items)
            for item in items:
                domain_type_counts[domain][item['type']] += 1

        # Count unclassified items
        unclassified_count = len(flat_items)

        # Detect conflicts
        conflicts = self.detect_conflicts(domains)

        # Calculate balance
        total = sum(domain_counts.values())
        if total > 0:
            personal_pct = (domain_counts.get(Domain.PERSONAL.value, 0) / total) * 100
            business_pct = (domain_counts.get(Domain.BUSINESS.value, 0) / total) * 100
            shared_pct = (domain_counts.get(Domain.SHARED.value, 0) / total) * 100
        else:
            personal_pct = business_pct = shared_pct = 0

        # Generate recommendations
        recommendations = []
        if personal_pct > 70:
            recommendations.append("⚠️ High personal task load - consider delegating or deferring non-urgent personal items")
        if business_pct > 70:
            recommendations.append("⚠️ High business task load - prioritize critical client work")
        if conflicts:
            recommendations.append(f"⚠️ {len(conflicts)} cross-domain conflicts detected - review conflicts section")
        if unclassified_count > 5:
            recommendations.append(f"📁 {unclassified_count} unclassified items - run domain classification to organize")

        return {
            'timestamp': datetime.now().isoformat(),
            'domain_counts': domain_counts,
            'domain_type_counts': {k.value: dict(v) for k, v in domain_type_counts.items()},
            'unclassified_count': unclassified_count,
            'total_items': total,
            'percentages': {
                'personal': round(personal_pct, 1),
                'business': round(business_pct, 1),
                'shared': round(shared_pct, 1)
            },
            'conflicts': conflicts,
            'recommendations': recommendations
        }

    def generate_report(self, output_file: str = None) -> str:
        """Generate a markdown report of cross-domain insights."""
        insights = self.generate_insights()

        report = f"""---
type: cross_domain_insights
generated: {insights['timestamp']}
---

# Cross-Domain Insights Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Overview

### Task Distribution

| Domain | Count | Percentage |
|--------|-------|------------|
| **Personal** | {insights['domain_counts'].get('personal', 0)} | {insights['percentages']['personal']}% |
| **Business** | {insights['domain_counts'].get('business', 0)} | {insights['percentages']['business']}% |
| **Shared** | {insights['domain_counts'].get('shared', 0)} | {insights['percentages']['shared']}% |
| **Unclassified** | {insights['unclassified_count']} | - |
| **Total** | {insights['total_items']} | 100% |

### Task Types by Domain

#### Personal Domain
"""

        # Add Personal task types
        personal_types = insights['domain_type_counts'].get('personal', {})
        if personal_types:
            for task_type, count in personal_types.items():
                report += f"- **{task_type}**: {count}\n"
        else:
            report += "- No items\n"

        report += "\n#### Business Domain\n"
        business_types = insights['domain_type_counts'].get('business', {})
        if business_types:
            for task_type, count in business_types.items():
                report += f"- **{task_type}**: {count}\n"
        else:
            report += "- No items\n"

        report += "\n#### Shared Domain\n"
        shared_types = insights['domain_type_counts'].get('shared', {})
        if shared_types:
            for task_type, count in shared_types.items():
                report += f"- **{task_type}**: {count}\n"
        else:
            report += "- No items\n"

        # Add conflicts section
        report += "\n---\n\n## Cross-Domain Conflicts\n\n"
        if insights['conflicts']:
            for conflict in insights['conflicts']:
                if conflict['type'] == 'time_conflict':
                    report += f"### ⚠️ Time Conflict at {conflict['time']}\n"
                    report += f"- **Personal:** {conflict['personal']['filename']}\n"
                    report += f"- **Business:** {conflict['business']['filename']}\n"
                    report += f"- **Action:** Reschedule one of these items\n\n"
                elif conflict['type'] == 'overload_warning':
                    report += f"### ⚠️ Overload Warning\n"
                    report += f"{conflict['message']}\n"
                    report += f"- **Action:** Prioritize items and consider deferring non-critical tasks\n\n"
        else:
            report += "✅ No conflicts detected\n\n"

        # Add recommendations
        report += "---\n\n## Recommendations\n\n"
        for rec in insights['recommendations']:
            report += f"{rec}\n\n"

        # Add work-life balance assessment
        report += "---\n\n## Work-Life Balance\n\n"
        personal_pct = insights['percentages']['personal']
        business_pct = insights['percentages']['business']

        if personal_pct > 60:
            report += "📊 **Assessment:** High personal load - ensure business priorities are not neglected\n"
        elif business_pct > 80:
            report += "📊 **Assessment:** High business load - consider scheduling personal time\n"
        elif 30 <= personal_pct <= 60 and 30 <= business_pct <= 70:
            report += "📊 **Assessment:** Good balance between personal and business domains\n"
        else:
            report += "📊 **Assessment:** Load is manageable\n"

        report += f"\n---\n\n*Generated by Cross-Domain Analyzer (Gold Tier Feature)*\n"

        # Write to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            print(f"Report saved to: {output_path}")

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate cross-domain insights for Personal and Business domains"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: vault/Briefings/Cross_Domain_Insights_YYYYMMDD.md)"
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print report to stdout"
    )

    args = parser.parse_args()

    # Generate output filename if not specified
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"AI_Employee_Vault/Briefings/Cross_Domain_Insights_{timestamp}.md"

    # Generate report
    analyzer = CrossDomainAnalyzer(args.vault)
    report = analyzer.generate_report(args.output)

    if args.print:
        print("\n" + "="*60)
        print("CROSS-DOMAIN INSIGHTS REPORT")
        print("="*60 + "\n")
        print(report)

    print(f"\n✅ Cross-domain insights generated: {args.output}")


if __name__ == "__main__":
    main()
