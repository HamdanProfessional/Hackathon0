"""
Enhanced Audit Logging System

Provides structured, comprehensive logging for all system events with support for:
- Structured log entries with consistent format
- Automatic log rotation and retention
- Security event logging
- Performance metrics logging
- Error tracking and debugging
- Audit trail for compliance

Usage:
    from audit_logging import AuditLogger
    logger = AuditLogger(vault_path=".")
    logger.log_action("email_sent", {...})
"""

import logging
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EventType(Enum):
    """
    Classification of event types for better filtering and analysis.
    """
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    ERROR = "error"
    DEGRADED = "degraded"
    RECOVERED = "recovered"
    ACTION = "action"
    SECURITY = "security"
    APPROVAL = "approval"
    PERFORMANCE = "performance"


class AuditLogger:
    """
    Comprehensive audit logging system.

    All logs follow the structured format defined in the reference documentation.
    Logs are stored in `/Logs/` directory with daily rotation.
    Retention period: 90 days (configurable).
    """

    def __init__(self, vault_path: str, retention_days: int = 90):
        """
        Initialize the audit logger.

        Args:
            vault_path: Path to Obsidian vault
            retention_days: Days to keep logs (default: 90 days)
        """
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / "Logs"
        self.retention_days = retention_days
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def log_action(
        self,
        action_type: str,
        component: str,
        details: Dict[str, Any],
        approval_status: Optional[str] = None,
        result: Optional[str] = None,
        confidence: Optional[str] = None,
        actor: str = "system"
    ) -> None:
        """
        Log an action event to the audit log.

        Args:
            action_type: Type of action (e.g., "email_sent", "watcher_started")
            component: Component that performed the action
            details: Dictionary of action details
            approval_status: Optional approval status
            result: Optional result description
            confidence: Confidence level (high/medium/low)
            actor: Who/what performed the action
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "event_type": EventType.ACTION.value,
            "actor": actor,
            "action_type": action_type,
            "details": details,
            "approval_status": approval_status,
            "result": result,
            "confidence": confidence,
        }

        self._write_log(log_entry)

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        component: str,
        details: Dict[str, Any],
        user: Optional[str] = None
    ) -> None:
        """
        Log a security event for compliance and auditing.

        Security events include:
        - Authentication attempts
        - Payment requests
        - New payee additions
        - Configuration changes
        - External connections

        Args:
            event_type: Type of security event (e.g., "authentication_attempt", "payment_request")
            severity: Severity level (critical, high, medium, low)
            component: Component involved
            details: Event details
            user: User associated with event (if applicable)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "event_type": EventType.SECURITY.value,
            "actor": user or "system",
            "action_type": event_type,
            "details": {
                "severity": severity,
                "details": details,
                "user": user or "system"
            },
        }

        self._write_log(log_entry)

    def log_performance_metric(
        self,
        component: str,
        metric_name: str,
        value: float,
        unit: str,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Log a performance metric for tracking and analysis.

        Args:
            component: Component being measured
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Optional list of tags for categorization
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "event_type": EventType.PERFORMANCE.value,
            "actor": "system",
            "action_type": metric_name,
            "details": {
                "value": value,
                "unit": unit,
                "tags": tags or []
            }
        }

        self._write_log(log_entry)

    def log_system_event(
        self,
        event: str,
        component: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log a system event (start/stop/restart/error/degraded/recovered).

        Args:
            event: System event type
            component: Component name
            details: Event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "action_type": event,
            "actor": "system",
            "details": details
        }

        self._write_log(log_entry)

    def _write_log(self, log_entry: Dict) -> None:
        """Write log entry to the appropriate daily log file."""
        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as error:
            logger.error(f"Failed to write log entry: {error}")

    def analyze_logs(self, days: int =  7) -> Dict[str, Any]:
        """
        Analyze logs from the last N days and generate summary.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with analysis results
        """
        results = {
            "period": f"Last {days} days",
            "total_events": 0,
            "by_type": {},
            "by_component": {},
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "errors": 0,
            "security_events": 0
        }

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for day_offset in range(days):
            log_file = self.logs_path / (end_date - timedelta(days=day_offset)).strftime("%Y-%m-%d.json")

            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                entry = json.loads(line)
                                results["total_events"] += 1

                                # Count by type
                                event_type = entry.get("action_type", "unknown")
                                results["by_type"][event_type] = results["by_type"].get(event_type, 0) + 1

                                # Count by component
                                component = entry.get("component", "unknown")
                                results["by_component"][component] = results["by_component"].get(component, 0) + 1

                                # Count severity (for security events)
                                if entry.get("action_type") == "security":
                                    results["security_events"] += 1
                                    severity = entry.get("details", {}).get("severity", "low")
                                    results["by_severity"][severity] += 1

                                # Count errors
                                if entry.get("action_type") == "error":
                                    results["errors"] += 1

                            except json.JSONDecodeError:
                                continue

                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")

        return results

    def generate_audit_report(self, days: int = 7) -> str:
        """
        Generate a comprehensive audit report for the last N days.

        Args:
            days: Number of days to include in report

        Returns:
            Formatted audit report as markdown
        """
        analysis = self.analyze_logs(days)

        report = f"""# Audit Report: Last {days} Days

**Period:** {analysis['period']}
**Total Events Logged:** {analysis['total_events']}

---

## Executive Summary

### Security Events
| Severity | Count | % of Total |
|----------|-------|------------|
| Critical | {analysis['by_severity']['critical']} | {(analysis['by_severity']['critical'] / max(1, analysis['total_events']) * 100):.1f}% |
| High | {analysis['by_severity']['high']} | {(analysis['by_severity']['high'] / max(1, analysis['total_events']) * 100):.1f}% |
| Medium | {analysis['by_severity']['medium']} | {(analysis['by_severity']['medium'] / max(1, analysis['total_events']) * 100):.1f}% |
| Low | {analysis['by_severity']['low']} | {(analysis['by_severity']['low'] / max(1, analysis['total_events']) * 100):.1f}% |

---

## Activity by Type

| Event Type | Count | % of Total |
|-----------|-------|------------|
"""

        # Add event types
        for event_type, count in sorted(analysis['by_type'].items(), key=lambda x: -x[1]):
            pct = (count / analysis['total_events']) * 100
            report += f"| {event_type:20} | {count:6} | {pct:.1f}%\n"

        report += f"""

---

## Activity by Component

| Component | Count | % of Total |
|-----------|-------|------------|
"""

        # Add components
        for component, count in sorted(analysis['by_component'].items(), key=lambda x: -x[1]):
            pct = (count / analysis['total_events']) * 100
            report += f"| {component:20} | {count:6} | {pct:.1f}%\n"

        report += f"""

---

## System Health

| Component | Errors | Status |
|-----------|--------|--------|
"""

        # Check each component
        for component in analysis['by_component'].keys():
            errors = 0
            status = "Healthy"
            report += f"| {component:20} | {errors:6} | {status}\n"

        report += f"""

---

## Security Events

Total Security Events: {analysis['security_events']}

---

## Recommendations

### Critical Items

### Improvements
-
"""

        # Add recommendations based on analysis
        if analysis['by_severity']['critical'] > 0:
            report += "### 🔴 Critical Items\n\n"
            for event in self._get_critical_events(analysis):
                report += f"- {event}\n"

        if analysis['by_type'].get('error', 0) > 10:
            report += "\n### ⚠️ High Error Rate\n\n"
            report += f"Your system has {analysis['by_type'].get('error', 0)} errors in the last {days} days.\n"
            report += "Consider reviewing error logs for recurring issues.\n"

        if analysis['by_type'].get('authentication', 0) > 0:
            report += "\n### 🔐 Authentication Issues\n\n"
            report += f"Detected {analysis['by_type'].get('authentication', 0)} authentication failures.\n"
            report += "Review credentials and token files.\n"

        report += f"""
---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Generated by Audit Logging System v1.0*
"""

        return report

    def _get_critical_events(self, analysis: Dict) -> List[str]:
        """Extract critical events from analysis."""
        critical_events = []
        log_file = self.logs_path / "current.json"

        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("action_type") == "security":
                            if entry.get("details", {}).get("severity") == "critical":
                                event_str = f"Critical: {entry['action_type']} in {entry['component']} - {entry.get('details', {}).get('user', 'system')}"
                                critical_events.append(event_str)
                    except json.JSONDecodeError:
                        continue

        return critical_events

    def cleanup_old_logs(self) -> None:
        """
        Remove log files older than retention period.
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed_count = 0

        for log_file in self.logs_path.glob("*.json"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Error removing old log file {log_file}: {e}")

        logger.info(f"Removed {removed_count} log files older than {self.retention_days} days")


class SecurityLogger:
    """
    Specialized logging for security-related events.

    Handles:
    - Authentication attempts (success/failure)
    - Payment requests
    - New payee additions
    - Configuration changes
    - External API connections
    - File operations outside vault
    """

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    def log_authentication_event(
        self,
        service: str,
        action: str,
        success: bool,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log authentication events for security audit.

        Args:
            service: Service being accessed (e.g., "Gmail", "Xero")
            action: Action performed (e.g., "login", "token_refresh", "logout")
            success: Whether authentication was successful
            details: Optional additional details
        """
        severity = "low" if success else "high"

        self.audit_logger.log_security_event(
            event_type=f"authentication_{action}",
            severity=severity,
            component=service,
            details={
                "service": service,
                "action": action,
                "success": success,
                **(details or {})
            }
        )

    def log_payment_event(
        self,
        amount: float,
        recipient: str,
        action: str,
        status: str,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log payment-related events.

        Security events include:
        - Payment requests
        - New payee additions
        - Payment confirmations
        - Payment failures

        Args:
            amount: Payment amount
            recipient: Payment recipient
            action: Action performed (request, confirm, fail)
            status: Status of payment action
            details: Optional additional details
        """
        self.audit_logger.log_security_event(
            event_type=f"payment_{action}",
            severity="critical",
            component="payment",
            details={
                "amount": amount,
                "recipient": recipient,
                "action": action,
                "status": status,
                **(details or {})
            }
        )

    def log_config_change(
        self,
        component: str,
        config_file: str,
        changed_keys: List[str],
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None
    ) -> None:
        """
        Log configuration changes for audit trail.

        Args:
            component: Component being configured
            config_file: Configuration file that changed
            changed_keys: List of keys that changed
            action: Action performed (update, delete, create)
            old_values: Original values of changed keys
            new_values: New values of changed keys
            user: User who made the change
        """
        self.audit_logger.log_security_event(
            event_type="config_change",
            severity="medium",
            component=component,
            details={
                "config_file": config_file,
                "action": action,
                "changed_keys": changed_keys,
                "old_values": old_values,
                "new_values": new_values,
                "user": user or "system"
            }
        )

    def log_file_operation(
        self,
        file_path: str,
        action: str,
        file_type: str,
        user: Optional[str] = None
    ) -> None:
        """
        Log file operations for security audit.

        Args:
            file_path: Path to file
            action: Action performed (create, delete, move, update)
            file_type: Type of file (email, image, document, code)
            user: User who performed the action
        """
        file_path_str = str(file_path)

        # Check if operation is outside vault
        vault_str = str(self.audit_logger.vault_path)
        is_external = not file_path_str.startswith(vault_str)

        severity = "medium" if is_external else "low"

        self.audit_logger.log_security_event(
            event_type="file_operation",
            severity=severity,
            component="filesystem",
            details={
                "action": action,
                "file_path": file_path_str,
                "is_external": is_external,
                "file_type": file_type,
                "user": user or "system"
            }
        )


class ComplianceLogger:
    """
    Logging for compliance and regulatory requirements.

    Handles:
    - Financial transaction logging
    - Email communication logging
    - Data processing operations
    - Third-party API calls
    - Data export events
    """

    def __init__(self, audit_logger: AuditLogger, business_name: str = "My Business"):
        self.audit_logger = audit_logger
        self.business_name = business_name

    def log_financial_transaction(
        self,
        transaction_type: str,
        amount: float,
        counterparty: str,
        action: str,
        status: str,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log financial transactions for compliance.

        This is critical for:
        - Audit requirements (SOX, GDPR, etc.)
        - Business expense tracking
        - Tax compliance

        Args:
            transaction_type: Type of transaction (payment_received, payment_sent, expense)
            amount: Transaction amount
            counterparty: Person or organization
            action: What was done (sent, received, spent)
            status: Status of transaction
            details: Additional details
        """
        self.audit_logger.log_action(
            action_type=f"financial_{transaction_type}",
            component="accounting",
            details={
                "transaction_type": transaction_type,
                "amount": amount,
                "counterparty": counterparty,
                "action": action,
                "status": status,
                "business": self.business_name,
                **(details or {})
            },
            approval_status="pending" if action == "payment_sent" else "completed"
        )

    def log_email_communication(
        self,
        direction: str,  # sent or received
        recipient: str,
        subject: str,
        has_attachments: bool,
        has_sensitive_data: bool,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log email communications for compliance.

        Email logging is essential for:
        - Regulatory compliance
        - Business communication records
        - Audit trails
        - Legal discovery

        Args:
            direction: "sent" or "received"
            recipient: Email recipient
            subject: Email subject
            has_attachments: Whether email has attachments
            has_sensitive_data: Whether email contains sensitive data
            details: Additional details
        """
        severity = "high" if has_sensitive_data else "low"

        self.audit_logger.log_security_event(
            event_type=f"email_{direction}",
            severity=severity,
            component="email",
            details={
                "direction": direction,
                "recipient": recipient,
                "subject": subject,
                "has_attachments": has_attachments,
                "has_sensitive_data": has_sensitive_data,
                **(details or {})
            }
        )

    def log_data_export(self, data_type: str, records_count: int, destination: str) -> None:
        """
        Log data export events for compliance.

        Args:
            data_type: Type of data exported
            records_count: Number of records
            destination: Destination of data export
        """
        self.audit_logger.log_security_event(
            event_type="data_export",
            severity="medium",
            component="data_export",
            details={
                "data_type": data_type,
                "records_count": records_count,
                "destination": destination,
                "source": "Personal AI Employee"
            }
        )


def main():
    """Command-line interface for audit logging utilities."""

    import argparse

    parser = argparse.ArgumentParser(description="Audit Logging utilities")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze logs command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze audit logs and generate report")
    analyze_parser.add_argument("--days", type=int, default=7, help="Number of days to analyze (default: 7)")
    analyze_parser.add_argument("--output", help="Output file for report")
    analyze_parser.add_argument("--vault", default=".", help="Path to vault")

    # Cleanup logs command
    cleanup_parser = subparsers.add_parser("cleanup", help="Remove old log files")
    cleanup_parser.add_argument("--vault", default=".", help="Path to vault")

    # Generate security report command
    security_parser = subparsers.add_parser("generate_security_report", help="Generate security report")
    security_parser.add_argument("--vault", default=".", help="Path to vault")
    security_parser.add_argument("--days", type=int, default=30, help="Days to analyze")

    args = parser.parse_args()

    # Execute the requested command
    if args.command == "analyze":
        logger = AuditLogger(args.vault)
        report = logger.generate_audit_report(days=args.days)
        if args.output:
            Path(args.output).write_text(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)

    elif args.command == "cleanup":
        logger = AuditLogger(args.vault)
        logger.cleanup_old_logs()
        print(f"Cleanup complete. Old logs removed based on retention policy (default 90 days)")

    elif args.command == "generate_security_report":
        logger = AuditLogger(args.vault)
        report = logger.analyze_logs(days=args.days)
        # Filter only security events
        print(f"\n=== Security Report (Last {args.days} days) ===\n")
        print(report)


if __name__ == "__main__":
    main()
