#!/usr/bin/env python3
"""
Workflow Validator - Validate complete workflows
"""

import argparse
from pathlib import Path


def validate_workflow(workflow_name: str, vault_path: str = "AI_Employee_Vault"):
    """Validate a workflow"""
    print(f"Validating {workflow_name} workflow...")

    vault = Path(vault_path)

    checks = [
        ("Needs_Action folder exists", (vault / "Needs_Action").exists()),
        ("Plans folder exists", (vault / "Plans").exists()),
        ("Pending_Approval folder exists", (vault / "Pending_Approval").exists()),
        ("Approved folder exists", (vault / "Approved").exists()),
        ("Done folder exists", (vault / "Done").exists()),
    ]

    all_pass = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_pass = False

    if all_pass:
        print(f"\n✅ {workflow_name} workflow validated")
    else:
        print(f"\n❌ {workflow_name} workflow has issues")

    return all_pass


def main():
    parser = argparse.ArgumentParser(description='Workflow Validator')
    parser.add_argument('--workflow', help='Workflow to validate')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Vault path')
    parser.add_argument('--all', action='store_true', help='Validate all workflows')

    args = parser.parse_args()

    print("🔍 Workflow Validator\n")

    if args.all:
        workflows = ['gmail', 'slack', 'whatsapp', 'calendar', 'xero']
        for wf in workflows:
            validate_workflow(wf, args.vault)
    elif args.workflow:
        validate_workflow(args.workflow, args.vault)
    else:
        print("Specify --workflow <name> or --all")


if __name__ == '__main__':
    main()
