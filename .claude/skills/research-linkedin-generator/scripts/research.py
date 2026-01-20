#!/usr/bin/env python3
"""
Research LinkedIn Generator - AI Employee Skill

Automatically research topics and generate professional LinkedIn posts.
Integrates with the AI Employee approval workflow.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ResearchLinkedInGenerator:
    """Research topics and generate LinkedIn posts"""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.plans_path = self.vault_path / "Plans"
        self.pending_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"

    def create_research_request(self, topic: str) -> Path:
        """Create a research request file in Inbox"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic.lower().replace(" ", "_")[:50]
        filename = f"RESEARCH_REQUEST_{timestamp}_{slug}.md"

        request_file = self.inbox_path / filename

        content = f"""---
type: research_request
action: research_and_linkedin_post
topic: {topic}
created: {datetime.now().isoformat()}
---

# Research Request: {topic}

Please research this topic and create a professional LinkedIn post.

## Research Requirements
- Search Google for recent articles (past 30 days)
- Analyze 8-10 relevant sources
- Extract key insights, statistics, and quotes
- Generate a 1,000-2,000 character LinkedIn post
- Cite all sources for statistics and quotes

## Output Format
- Professional tone
- Include hook, body, call-to-action
- Add 5-10 relevant hashtags
- Cite sources inline

## Approval
The generated post will require approval before posting.
"""

        request_file.parent.mkdir(parents=True, exist_ok=True)
        request_file.write_text(content)

        print(f"✓ Research request created: {request_file}")
        return request_file

    def process_inbox_requests(self):
        """Process all research requests in Inbox"""
        requests = list(self.inbox_path.glob("RESEARCH_REQUEST_*.md"))

        if not requests:
            print("No research requests found in Inbox")
            return

        print(f"Found {len(requests)} research request(s)")

        for request_file in requests:
            print(f"\nProcessing: {request_file.name}")

            # Parse request
            content = request_file.read_text()
            topic = self._extract_topic(content)

            if topic:
                self._process_research(topic, request_file)
            else:
                print(f"  ✗ Could not extract topic from request")

    def _extract_topic(self, content: str) -> str:
        """Extract topic from request file"""
        for line in content.split('\n'):
            if line.startswith('topic: '):
                return line.split(':', 1)[1].strip()
        return None

    def _process_research(self, topic: str, request_file: Path):
        """Process research for a topic (placeholder for implementation)"""
        print(f"  Topic: {topic}")
        print("  → This would trigger browser automation to:")
        print("     1. Search Google for the topic")
        print("     2. Extract content from 8-10 sources")
        print("     3. Analyze and synthesize findings")
        print("     4. Generate LinkedIn post")
        print("     5. Create approval file in Pending_Approval/")

        # Move request to Plans to indicate it's being processed
        plan_file = self.plans_path / request_file.name.replace("REQUEST", "")
        request_file.rename(plan_file)
        print(f"  ✓ Moved to Plans/: {plan_file.name}")

        # Note: In production, this would:
        # 1. Use Playwright MCP to search Google
        # 2. Visit each source and extract content
        # 3. Use GLM-4.7 to analyze and generate post
        # 4. Create approval file in Pending_Approval/


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Research LinkedIn Generator - AI Employee Skill"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--topic",
        help="Topic to research (creates request in Inbox)"
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process all requests in Inbox"
    )

    args = parser.parse_args()

    generator = ResearchLinkedInGenerator(args.vault)

    if args.topic:
        print(f"Creating research request for: {args.topic}")
        generator.create_research_request(args.topic)
        print("\nNext steps:")
        print("1. The AI Employee will process this request")
        print("2. Research will be saved to Plans/")
        print("3. LinkedIn post will be created in Pending_Approval/")
        print("4. Review and move to Approved/ to publish")

    elif args.process:
        print("Processing research requests...")
        generator.process_inbox_requests()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
