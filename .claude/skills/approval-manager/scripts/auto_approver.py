#!/usr/bin/env python3
"""
AI-Powered Auto-Approval Processor for AI Employee

Uses Claude AI to intelligently decide which actions to auto-approve
based on Company_Handbook.md rules and context.

Usage:
    python scripts/auto_approver.py --vault AI_Employee_Vault
"""

import json
import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import yaml


class AIApprover:
    """AI-powered approval decisions using Claude."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.rejected = self.vault_path / "Rejected"
        self.done = self.vault_path / "Done"

        # Ensure folders exist
        for folder in [self.needs_action, self.pending_approval, self.approved, self.rejected, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # Load Company Handbook rules
        self.handbook_rules = self._load_handbook_rules()

        # Load API key from environment
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def _load_handbook_rules(self) -> str:
        """Load Company_Handbook.md to provide context to Claude."""
        handbook_path = self.vault_path / "Company_Handbook.md"

        if handbook_path.exists():
            return handbook_path.read_text(encoding='utf-8')
        else:
            return """
# Default Company Handbook Rules

## Permission Boundaries
- Auto-approve: Routine tasks, file operations, known contact emails
- Manual review required: Payments, social media, new contacts, high-value actions
- Reject: Scams, phishing, dangerous actions

## Safety First
When in doubt, require manual review. It's better to ask for approval than to make a mistake.
"""

    def _ask_claude_for_decision(self, frontmatter: Dict, content: str, filepath: Path) -> str:
        """
        Ask Claude AI to make an approval decision.

        Returns:
            "approve" - Safe to auto-approve
            "reject" - Unsafe, should be rejected
            "manual" - Needs human review
        """
        if not self.api_key:
            # Fallback to simple rules if no API key
            return self._fallback_decision(frontmatter, content, filepath)

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            # Build prompt with context
            prompt = f"""You are an AI assistant that decides whether to auto-approve actions based on company rules.

# COMPANY HANDBOOK RULES
{self.handbook_rules[:3000]}  # First 3000 chars of rules

# ACTION TO EVALUATE
Type: {frontmatter.get('type', 'unknown')}
Service: {frontmatter.get('service', 'unknown')}
Priority: {frontmatter.get('priority', 'normal')}
From: {frontmatter.get('from', 'unknown')}
Subject: {frontmatter.get('subject', 'N/A')}

# CONTENT
{content[:2000]}  # First 2000 chars

# YOUR TASK
Decide: approve, reject, or manual

Rules:
1. "approve" - Safe routine actions (file ops, known contacts, low-risk tasks)
2. "reject" - Scams, phishing, clearly dangerous actions
3. "manual" - Everything uncertain (social media, payments, new contacts)

Respond with ONLY ONE WORD: approve, reject, or manual
"""

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            decision = message.content[0].text.strip().lower()

            # Validate response
            if decision in ["approve", "reject", "manual"]:
                return decision
            else:
                print(f"[WARNING] Claude returned unexpected decision: {decision}")
                return "manual"  # Default to manual review

        except Exception as e:
            print(f"[WARNING] AI decision failed: {e}, using fallback")
            return self._fallback_decision(frontmatter, content, filepath)

    def _fallback_decision(self, frontmatter: Dict, content: str, filepath: Path) -> str:
        """Fallback rule-based decision if AI is unavailable."""
        action_type = frontmatter.get("type", "")
        service = frontmatter.get("service", "")
        priority = frontmatter.get("priority", "normal")
        subject = frontmatter.get("subject", "").lower()
        content_lower = content.lower()

        # REJECT: Payments and scams
        if any(word in subject or word in content_lower for word in ["invoice", "payment", "urgent", "wire transfer", "bitcoin"]):
            return "reject"

        # MANUAL: Social media (always)
        if action_type in ["linkedin_post", "twitter_post", "instagram_post", "facebook_post"]:
            return "manual"

        # MANUAL: High priority
        if priority == "high" or priority == "!!!":
            return "manual"

        # APPROVE: File drops
        if action_type == "file_drop":
            return "approve"

        # MANUAL: Unknown emails
        if action_type == "email" or service == "gmail":
            return "manual"  # Better to review emails

        # APPROVE: Slack/WhatsApp messages (just notifications)
        if action_type in ["slack_message", "whatsapp_message"]:
            return "approve"

        # Default: Manual review
        return "manual"

    def process_needs_action(self) -> Dict[str, int]:
        """
        Process all items in Needs_Action/ and Inbox/ using AI decisions.

        Returns:
            Dictionary with counts of processed items
        """
        results = {
            "auto_approved": 0,
            "requires_approval": 0,
            "rejected": 0,
            "errors": 0
        }

        # Process both Needs_Action and Inbox
        files = list(self.needs_action.glob("*.md")) + list((self.vault_path / "Inbox").glob("*.md"))

        for filepath in files:
            try:
                # Read file content
                content = filepath.read_text(encoding='utf-8')
                frontmatter = self._extract_frontmatter(filepath)

                if frontmatter.get("status") == "pending":
                    # Ask AI for decision
                    print(f"\n[AI] Analyzing: {filepath.name}")
                    decision = self._ask_claude_for_decision(frontmatter, content, filepath)

                    print(f"[AI] Decision: {decision.upper()}")

                    if decision == "approve":
                        self._auto_approve(filepath, frontmatter)
                        results["auto_approved"] += 1
                        print(f"[AUTO-APPROVE] {filepath.name}")

                    elif decision == "reject":
                        # Move to Rejected
                        dest = self.rejected / filepath.name
                        shutil.move(str(filepath), str(dest))
                        results["rejected"] += 1
                        print(f"[REJECTED] {filepath.name} - unsafe action")

                    else:
                        # Requires manual approval - move to Pending_Approval
                        dest = self.pending_approval / filepath.name
                        shutil.move(str(filepath), str(dest))
                        results["requires_approval"] += 1
                        print(f"[MANUAL REVIEW] {filepath.name}")

            except Exception as e:
                print(f"[ERROR] Failed to process {filepath.name}: {e}")
                results["errors"] += 1

        return results

    def _auto_approve(self, filepath: Path, frontmatter: Dict):
        """Auto-approve an action by moving to Approved/."""
        dest = self.approved / filepath.name

        # Update frontmatter
        frontmatter["status"] = "approved"
        frontmatter["auto_approved"] = True
        frontmatter["approved_at"] = datetime.now().isoformat()
        frontmatter["approved_by"] = "AI (Claude)"

        # Write updated frontmatter
        content = filepath.read_text(encoding='utf-8')
        updated_content = self._update_frontmatter(content, frontmatter)

        # Write to Approved folder
        dest.write_text(updated_content, encoding='utf-8')

        # Delete from Needs_Action
        filepath.unlink()

        print(f"   → Auto-approved and moved to Approved/")

    def _extract_frontmatter(self, filepath: Path) -> Dict:
        """Extract YAML frontmatter from markdown file, or create metadata for plain text files."""
        content = filepath.read_text(encoding='utf-8')

        if content.startswith("---"):
            # Find end of frontmatter
            try:
                end = content.index("---", 3)
                frontmatter_text = content[3:end]
                import yaml
                return yaml.safe_load(frontmatter_text) or {}
            except (ValueError, yaml.YAMLError):
                pass

        # No frontmatter - create metadata for plain text files
        return {
            "type": "file_drop",
            "status": "pending",
            "created": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            "original_name": filepath.name,
            "source": "inbox"
        }

    def _update_frontmatter(self, content: str, updates: Dict) -> str:
        """Update YAML frontmatter in markdown content."""
        if content.startswith("---"):
            try:
                end = content.index("---", 3)
                old_frontmatter = content[3:end]
                import yaml
                frontmatter = yaml.safe_load(old_frontmatter) or {}
                frontmatter.update(updates)

                # Build new frontmatter
                new_frontmatter = "---\n"
                for key, value in frontmatter.items():
                    if isinstance(value, (list, dict)):
                        import yaml
                        new_frontmatter += yaml.dump(value, default_flow_style=False)
                    else:
                        new_frontmatter += f"{key}: {value}\n"

                new_frontmatter += "---"

                # Return updated content
                return new_frontmatter + content[end + 3:]
            except (ValueError, yaml.YAMLError):
                pass

        return content


def main():
    """Main entry point."""
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description="AI-powered auto-approval using Claude"
    )
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("AI-POWERED AUTO-APPROVAL PROCESSOR")
    print("="*60)
    print(f"\nVault: {args.vault}")
    print(f"Rules from: Company_Handbook.md")
    print(f"AI: Claude 3 Haiku")
    print(f"Mode: {'Run once' if args.once else 'Continuous (every 2 minutes)'}\n")

    approver = AIApprover(args.vault)

    def run_once():
        print("[*] Processing Needs_Action/ with AI decisions...\n")

        results = approver.process_needs_action()

        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Auto-approved: {results['auto_approved']}")
        print(f"Requires manual review: {results['requires_approval']}")
        print(f"Rejected: {results['rejected']}")
        print(f"Errors: {results['errors']}")
        print("="*60 + "\n")

        return results

    # Run once if requested
    if args.once:
        results = run_once()
        return 0

    # Otherwise run continuously
    try:
        while True:
            results = run_once()
            # Wait 2 minutes before next check
            print("[*] Waiting 2 minutes until next check...\n")
            time.sleep(120)
    except KeyboardInterrupt:
        print("\n[INFO] Auto-approver stopped")
        return 0


if __name__ == "__main__":
    main()
