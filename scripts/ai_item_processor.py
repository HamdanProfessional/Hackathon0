#!/usr/bin/env python3
"""
AI Item Processor - Processes items using Claude API directly

This is a lightweight alternative to the orchestrator that doesn't require
invoking the full Claude Code CLI (which has memory issues).

Instead, it uses the Anthropic API directly to process items.
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import anthropic

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class AIItemProcessor:
    """
    Process items from Needs_Action/ using Claude API.

    This is the core of the AI Employee - it uses Claude to:
    1. Read and understand items
    2. Make decisions about what to do
    3. Create approval requests or execute safe actions
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress = self.vault_path / "In_Progress"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.done = self.vault_path / "Done"

        # Create folders
        for folder in [self.needs_action, self.in_progress,
                       self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            # Try to load from .env file
            env_file = project_root / ".env"
            if env_file.exists():
                import re
                for line in env_file.read_text().splitlines():
                    match = re.match(r'ANTHROPIC_API_KEY=(.+)', line)
                    if match:
                        api_key = match.group(1).strip().strip('"\'')
                        break

        if not api_key:
            # For testing, allow a placeholder if in test mode
            api_key = os.environ.get("ANTHROPIC_API_KEY_TEST", "sk-ant-test")

        self.client = anthropic.AsyncAnthropic(api_key=api_key)

        # State tracking
        self.processed_items = set()
        self.state_file = self.vault_path / ".ai_processor_state.json"
        self._load_state()

        # Logging
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'ai_processor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_state(self):
        """Load processed items from state file."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                self.processed_items = set(data.get("processed_items", []))
            except Exception:
                pass

    def _save_state(self):
        """Save processed items to state file."""
        try:
            data = {
                "processed_items": list(self.processed_items),
                "last_updated": datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def _get_new_items(self) -> List[Path]:
        """Get new items from Needs_Action that haven't been processed."""
        if not self.needs_action.exists():
            return []

        all_items = list(self.needs_action.rglob("*.md"))
        new_items = [
            item for item in all_items
            if item.name not in self.processed_items
        ]

        return sorted(new_items, key=lambda p: p.stat().st_mtime)

    def _fallback_decision(self, item_path: Path) -> Dict[str, Any]:
        """
        Make a decision without using Claude API (rule-based fallback).

        This is used when ANTHROPIC_API_KEY is not available.
        """
        item_content = item_path.read_text()
        item_name = item_path.name.lower()

        # Simple rule-based decision
        if "email" in item_name:
            return {
                "decision": "manual",
                "reasoning": "Email requires human review (fallback mode)",
                "actions": ["Review email content", "Decide on response"],
                "move_to": "Pending_Approval"
            }
        elif any(x in item_name for x in ["twitter", "linkedin", "facebook", "instagram"]):
            return {
                "decision": "manual",
                "reasoning": "Social media post requires human review (fallback mode)",
                "actions": ["Review post content", "Approve or reject"],
                "move_to": "Pending_Approval"
            }
        elif "test" in item_name.lower():
            return {
                "decision": "approve",
                "reasoning": "Test item approved (fallback mode)",
                "actions": ["Process test item"],
                "move_to": "Done"
            }
        else:
            return {
                "decision": "manual",
                "reasoning": "Unknown item type requires human review (fallback mode)",
                "actions": ["Review item"],
                "move_to": "Pending_Approval"
            }

    async def _process_item_with_claude(self, item_path: Path) -> Dict[str, Any]:
        """
        Process an item using Claude API.

        Returns a dict with:
        - decision: "approve", "reject", "manual"
        - reasoning: explanation of the decision
        - actions: list of actions to take
        """
        # Check if we have a valid API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key or api_key == "sk-ant-test":
            self.logger.info("No valid API key, using fallback decision")
            return self._fallback_decision(item_path)

        # Read the item
        item_content = item_path.read_text()
        item_name = item_path.name
        item_relative = item_path.relative_to(self.vault_path)

        # Read context files
        dashboard_content = ""
        dashboard_file = self.vault_path / "Dashboard.md"
        if dashboard_file.exists():
            dashboard_content = dashboard_file.read_text()

        handbook_content = ""
        handbook_file = self.vault_path / "Company_Handbook.md"
        if handbook_file.exists():
            handbook_content = handbook_file.read_text()

        # Create the prompt for Claude
        system_prompt = """You are an AI Employee processing tasks from a task queue.

Your job is to:
1. Read and understand the task
2. Decide what action to take
3. Execute the action or request approval

Decisions:
- "approve" - Safe actions that can be done automatically (file operations, known contacts, routine tasks)
- "manual" - Requires human review (social media posts, payments, new contacts, important decisions)
- "reject" - Dangerous or inappropriate (scams, phishing, requests that violate policy)

Be thorough and thoughtful. Consider the context from Dashboard.md and Company_Handbook.md."""

        user_message = f"""# Task to Process

**File:** {item_relative}

**Content:**
```
{item_content}
```

---

**Context from Dashboard:**
```
{dashboard_content[:2000] if dashboard_content else "No dashboard available"}
```

**Context from Company Handbook:**
```
{handbook_content[:2000] if handbook_content else "No handbook available"}
```

---

Analyze this task and provide your response in the following JSON format:

```json
{{
  "decision": "approve|manual|reject",
  "reasoning": "Brief explanation of your decision",
  "actions": ["List of actions to take"],
  "new_file_content": "If creating a new file, put content here (optional)",
  "move_to": "Where to move the file (Pending_Approval/Approved/Done/Rejected)"
}}
```

Think step by step:
1. What type of task is this?
2. What action is needed?
3. Is it safe to automate or does it need human review?
4. What should be done?

Respond ONLY with valid JSON, no other text."""

        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            response_text = response.content[0].text

            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)

            result = json.loads(response_text)
            return result

        except Exception as e:
            self.logger.error(f"Error processing with Claude: {e}")
            return {
                "decision": "manual",
                "reasoning": f"Error during processing: {e}",
                "actions": [],
                "move_to": "Pending_Approval"
            }

    async def _process_item(self, item_path: Path):
        """Process a single item."""
        item_name = item_path.name

        # Move to in-progress first
        in_progress = self.in_progress / item_name
        item_path.rename(in_progress)

        self.logger.info(f"Processing: {item_name}")

        try:
            # Get Claude's decision
            result = await self._process_item_with_claude(in_progress)

            self.logger.info(f"Decision: {result['decision']} - {result.get('reasoning', '')}")

            # Execute the decision
            move_to = result.get("move_to")

            if result["decision"] == "reject":
                move_to = "Rejected"
            elif result["decision"] == "manual":
                move_to = "Pending_Approval"
            elif result["decision"] == "approve":
                # For approved items, create execution file or move to Approved
                move_to = "Approved"

            # Move the file
            if move_to:
                target_folder = self.vault_path / move_to
                target_folder.mkdir(parents=True, exist_ok=True)
                target_path = target_folder / item_name

                if in_progress.exists():
                    in_progress.rename(target_path)
                    self.logger.info(f"Moved to {move_to}/: {item_name}")

            # Mark as processed
            self.processed_items.add(item_name)
            self._save_state()

            # Create summary in Briefings
            self._create_summary(item_name, result)

        except Exception as e:
            self.logger.error(f"Error processing item: {e}")
            # Move back to needs_action
            if in_progress.exists():
                item_path.rename(self.needs_action / item_name)

    def _create_summary(self, item_name: str, result: Dict[str, Any]):
        """Create a summary of the processing decision."""
        briefings_dir = self.vault_path / "Briefings"
        briefings_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = briefings_dir / f"AI_Processing_{timestamp}.md"

        content = f"""# AI Processing Summary: {item_name}

**Date:** {datetime.now().isoformat()}
**Decision:** {result.get('decision', 'unknown')}

## Reasoning
{result.get('reasoning', 'No reasoning provided')}

## Actions
{chr(10).join('- ' + a for a in result.get('actions', [])) or 'No actions listed'}

## File Location
Moved to: {result.get('move_to', 'Unknown')}

---

*Processed by AI Employee using Claude 3 Haiku*
"""
        summary_file.write_text(content)

    async def run_once(self):
        """Run one processing cycle."""
        self.logger.info("=" * 60)
        self.logger.info("AI Item Processor - Checking for new items")
        self.logger.info("=" * 60)

        new_items = self._get_new_items()

        if not new_items:
            self.logger.info("No new items to process")
            return

        self.logger.info(f"Found {len(new_items)} new items")

        # Process each item
        for item_path in new_items:
            await self._process_item(item_path)
            # Small delay between items to avoid rate limits
            await asyncio.sleep(2)

    async def run(self):
        """Run continuous loop."""
        self.logger.info("[START] Starting AI Item Processor")
        self.logger.info(f"[DIR] Vault: {self.vault_path}")

        try:
            while True:
                await self.run_once()
                self.logger.info("Waiting 60 seconds before next check...")
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("[STOP] Stopped by user")
        except Exception as e:
            self.logger.error(f"[FATAL] Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Item Processor - Process items with Claude API"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to vault (default: AI_Employee_Vault)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )

    args = parser.parse_args()

    processor = AIItemProcessor(vault_path=args.vault)

    if args.once:
        asyncio.run(processor.run_once())
    else:
        asyncio.run(processor.run())


if __name__ == "__main__":
    main()
