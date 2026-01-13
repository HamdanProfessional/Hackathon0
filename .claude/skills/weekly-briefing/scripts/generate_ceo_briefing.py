#!/usr/bin/env python3
"""
Weekly CEO Briefing Generator

Analyzes the past week's activity and generates a comprehensive
Monday Morning CEO Briefing.

Usage:
    python generate_ceo_briefing.py [--vault PATH] [--weeks N]
"""

import argparse
import json
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class WeeklyBriefingGenerator:
    """Generate CEO briefings from vault data."""

    # Subscription patterns
    SUBSCRIPTION_PATTERNS = {
        "netflix.com": "Netflix",
        "spotify.com": "Spotify",
        "adobe.com": "Adobe Creative Cloud",
        "notion.so": "Notion",
        "slack.com": "Slack",
        "openai.com": "OpenAI/ChatGPT",
        "google.com": "Google Services",
    }

    def __init__(self, vault_path: str, weeks_back: int = 1):
        self.vault_path = Path(vault_path)
        self.weeks_back = weeks_back

        # Folder paths
        self.business_goals_path = self.vault_path / "Business_Goals.md"
        self.accounting_path = self.vault_path / "Accounting"
        self.done_path = self.vault_path / "Done"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.logs_path = self.vault_path / "Logs"
        self.briefings_path = self.vault_path / "Briefings"

        # Ensure Briefings folder exists
        self.briefings_path.mkdir(parents=True, exist_ok=True)

        # Date range
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(weeks=weeks_back)

    def extract_business_goals(self) -> dict:
        """Extract revenue targets and metrics from Business_Goals.md."""
        if not self.business_goals_path.exists():
            return {"monthly_goal": 0, "metrics": {}}

        content = self.business_goals_path.read_text(encoding="utf-8")

        # Extract monthly revenue goal
        goal_match = re.search(r'Monthly goal:\s*\$?([\d,]+)', content)
        monthly_goal = int(goal_match.group(1).replace(",", "")) if goal_match else 0

        return {
            "monthly_goal": monthly_goal,
            "metrics": {}
        }

    def analyze_accounting(self) -> dict:
        """Analyze accounting folder for revenue and expenses."""
        accounting_data = {
            "revenue": 0,
            "expenses": 0,
            "invoices_sent": 0,
            "invoices_paid": 0,
            "subscriptions": [],
        }

        if not self.accounting_path.exists():
            return accounting_data

        # This is a placeholder - real implementation would parse
        # actual accounting files. For now, return empty data.
        logger.info("Accounting folder exists - implementation pending for file parsing")

        return accounting_data

    def analyze_done_folder(self) -> dict:
        """Analyze completed work."""
        done_items = []

        if not self.done_path.exists():
            return {"completed": 0, "by_category": defaultdict(int)}

        # Count completed items
        for filepath in self.done_path.glob("*.md"):
            try:
                stat = filepath.stat()
                # Check if modified within date range
                mtime = datetime.fromtimestamp(stat.st_mtime)
                if self.start_date <= mtime <= self.end_date:
                    # Categorize
                    category = self._categorize_file(filepath)
                    done_items.append({
                        "filename": filepath.name,
                        "category": category,
                        "completed_date": mtime.strftime("%Y-%m-%d"),
                    })
            except Exception as e:
                logger.warning(f"Error reading {filepath.name}: {e}")

        by_category = defaultdict(int)
        for item in done_items:
            by_category[item["category"]] += 1

        return {
            "completed": len(done_items),
            "by_category": dict(by_category),
            "items": done_items[-10:]  # Last 10 items
        }

    def _categorize_file(self, filepath: Path) -> str:
        """Categorize a file by type."""
        name_lower = filepath.name.lower()

        if "email" in name_lower:
            return "Email"
        elif "task" in name_lower:
            return "Task"
        elif "event" in name_lower or "calendar" in name_lower:
            return "Event"
        elif "payment" in name_lower or "invoice" in name_lower:
            return "Financial"
        else:
            return "Other"

    def analyze_logs(self) -> dict:
        """Analyze activity logs."""
        log_data = {
            "total_actions": 0,
            "by_type": defaultdict(int),
            "errors": 0,
        }

        if not self.logs_path.exists():
            return log_data

        # Parse log files in date range
        current_date = self.start_date
        while current_date <= self.end_date:
            log_file = self.logs_path / current_date.strftime("%Y-%m-%d.json")

            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                try:
                                    entry = json.loads(line)
                                    log_data["total_actions"] += 1
                                    action_type = entry.get("action_type", "unknown")
                                    log_data["by_type"][action_type] += 1

                                    if action_type == "error":
                                        log_data["errors"] += 1
                                except json.JSONDecodeError:
                                    continue
                except Exception as e:
                    logger.warning(f"Error reading {log_file.name}: {e}")

            current_date += timedelta(days=1)

        return log_data

    def detect_bottlenecks(self) -> list:
        """Detect bottlenecks from Needs_Action folder."""
        bottlenecks = []

        if not self.needs_action_path.exists():
            return bottlenecks

        for filepath in self.needs_action_path.glob("*.md"):
            try:
                stat = filepath.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                age_days = (datetime.now() - mtime).days

                # Flag items older than 3 days
                if age_days > 3:
                    bottlenecks.append({
                        "filename": filepath.name,
                        "age_days": age_days,
                        "reason": f"Has been in Needs_Action for {age_days} days"
                    })
            except Exception as e:
                logger.warning(f"Error reading {filepath.name}: {e}")

        return sorted(bottlenecks, key=lambda x: x["age_days"], reverse=True)[:5]

    def generate_briefing(self) -> str:
        """Generate the CEO briefing content."""
        # Collect data
        goals = self.extract_business_goals()
        accounting = self.analyze_accounting()
        done_analysis = self.analyze_done_folder()
        log_analysis = self.analyze_logs()
        bottlenecks = self.detect_bottlenecks()

        # Calculate dates
        period_start = self.start_date.strftime("%Y-%m-%d")
        period_end = self.end_date.strftime("%Y-%m-%d")
        week_number = self.end_date.isocalendar()[1]

        # Build the briefing
        briefing = f"""---
generated: {datetime.now().isoformat()}
period: {period_start} to {period_end}
week_number: {week_number}
---

# Monday Morning CEO Briefing

## Executive Summary

"""

        # Executive summary (placeholder - would be generated by AI)
        briefing += f"Week {week_number} completed with {done_analysis['completed']} items finished. "
        briefing += f"Total activity logged: {log_analysis['total_actions']} actions. "
        if bottlenecks:
            briefing += f"⚠️ {len(bottlenecks)} items require attention (bottlenecks detected). "
        else:
            briefing += "✅ No bottlenecks identified. "

        # Revenue section
        briefing += f"""

## Revenue

### This Week
| Metric | Amount | Change vs Last Week |
|--------|--------|-------------------|
| Revenue | ${accounting['revenue']:,.2f} | - |
| Invoices Sent | {accounting['invoices_sent']} | - |
| Invoices Paid | {accounting['invoices_paid']} | - |

### Month to Date
| Metric | MTD | Goal | Progress |
|--------|-----|------|----------|
| Revenue | ${accounting['revenue']:,.2f} | ${goals['monthly_goal']:,.2f} | {min(100, int(accounting['revenue'] / goals['monthly_goal'] * 100)) if goals['monthly_goal'] > 0 else 0}% |

---

## Completed Work

### By Category
| Category | Count |
|----------|-------|
"""

        for category, count in done_analysis['by_category'].items():
            briefing += f"| {category} | {count} |\n"

        briefing += "\n### Recent Completions\n"
        if done_analysis['items']:
            for item in done_analysis['items'][-5:]:
                briefing += f"- [x] {item['filename']} (completed: {item['completed_date']})\n"
        else:
            briefing += "- [x] No items completed this week\n"

        # Bottlenecks
        briefing += "\n---\n\n## Bottlenecks\n"

        if bottlenecks:
            briefing += "| Task | Age | Reason |\n"
            briefing += "|------|-----|--------|\n"
            for bottleneck in bottlenecks:
                briefing += f"| {bottleneck['filename'][:40]} | {bottleneck['age_days']} days | {bottleneck['reason']} |\n"
        else:
            briefing += "✅ No bottlenecks identified this week.\n"

        # Activity summary
        briefing += "\n---\n\n## Activity Summary\n\n"
        briefing += f"Total Actions Logged: {log_analysis['total_actions']}\n\n"

        if log_analysis['by_type']:
            briefing += "### Actions by Type\n"
            for action_type, count in sorted(log_analysis['by_type'].items(), key=lambda x: -x[1]):
                briefing += f"- {action_type}: {count}\n"

        # Upcoming focus
        briefing += "\n---\n\n## Focus for This Week\n\n"
        briefing += "1. [ ] Review and clear pending bottlenecks\n"
        briefing += "2. [ ] Process any outstanding items in Needs_Action\n"
        briefing += "3. [ ] Review subscription costs and optimize\n"
        briefing += "4. [ ] Update business goals if needed\n"

        briefing += "\n---\n"
        briefing += f"\n*Generated by Personal AI Employee v0.1 on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"

        return briefing

    def save_briefing(self) -> Path:
        """Generate and save the CEO briefing."""
        briefing_content = self.generate_briefing()

        # Filename with Monday's date
        monday = self.end_date - timedelta(days=self.end_date.weekday())
        filename = f"{monday.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        briefing_path = self.briefings_path / filename

        briefing_path.write_text(briefing_content, encoding="utf-8")
        logger.info(f"CEO Briefing saved to {briefing_path}")

        return briefing_path


def main():
    parser = argparse.ArgumentParser(description="Generate weekly CEO briefing")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to vault (default: current directory)"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=1,
        help="Number of weeks to analyze (default: 1)"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output to stdout instead of file"
    )

    args = parser.parse_args()

    generator = WeeklyBriefingGenerator(args.vault, args.weeks)

    if args.stdout:
        print(generator.generate_briefing())
    else:
        briefing_path = generator.save_briefing()
        print(f"Briefing saved to: {briefing_path}")


if __name__ == "__main__":
    main()
