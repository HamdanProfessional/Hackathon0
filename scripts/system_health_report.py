#!/usr/bin/env python3
"""
System Health Report Generator

Generates a comprehensive health report for the AI Employee system,
including Cloud VM status, Local status, git sync status, and recommendations.
"""
import argparse
import json
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class HealthReportGenerator:
    """Generates system health reports for AI Employee system."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "cloud": {},
            "local": {},
            "git_sync": {},
            "recommendations": [],
        }

    def run_command(self, cmd: List[str], ssh: bool = False) -> str:
        """Run a command locally or via SSH."""
        # On Windows, pm2 is actually pm2.cmd
        if not ssh and platform.system() == "Windows" and cmd[0] == "pm2":
            cmd = ["pm2.cmd"] + cmd[1:]

        if ssh:
            cmd = ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                    "root@143.244.143.143"] + [" ".join(cmd)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                      timeout=30, encoding='utf-8', errors='replace')
            return result.stdout or ""
        except subprocess.TimeoutExpired:
            return "Error: Command timeout"
        except Exception as e:
            return f"Error: {e}"

    def _strip_ansi_codes(self, text: str) -> str:
        """Remove ANSI color codes from text."""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\033\[[0-9;]*m|\[1m|\[36m|\[39m|\[22m|\[27m|\[7m|\[31m|\[32m|\[90m')
        return ansi_escape.sub('', text)

    def parse_pm2_status(self, output: str) -> Dict[str, Any]:
        """Parse PM2 status text output into structured data.

        PM2 status table structure (after splitting by │):
        [0]: empty (before first │)
        [1]: id
        [2]: name
        [3]: namespace
        [4]: version
        [5]: mode
        [6]: pid
        [7]: uptime
        [8]: restarts (↺)
        [9]: status
        [10]: cpu
        [11]: memory
        ...
        """
        processes = {}
        for line in output.split('\n'):
            # Remove ANSI color codes that interfere with parsing
            line = self._strip_ansi_codes(line)

            # Look for lines with process status (│ character and "online"/"stopped")
            if "│" in line and ("online" in line.lower() or "stopped" in line.lower()):
                # Extract process columns
                parts = line.split('│')

                if len(parts) >= 12:
                    # Extract columns based on actual table structure
                    # parts[1] = ID, parts[2] = Name, etc.
                    try:
                        proc_id = parts[1].strip()
                        name = parts[2].strip()

                        # Skip header rows
                        if not name or name.lower() in ("name", "namespace", "────", "id"):
                            continue

                        # Find status (column 9)
                        status = "unknown"
                        if len(parts) > 9:
                            status_col = parts[9].strip().lower()
                            if "online" in status_col:
                                status = "online"
                            elif "stopped" in status_col or "errored" in status_col:
                                status = "stopped"
                            elif "launching" in status_col:
                                status = "launching"

                        # Extract restart count (column 8, has ↺ symbol)
                        restarts = 0
                        if len(parts) > 8:
                            restart_str = parts[8].strip().replace("↺", "").replace("━", "").strip()
                            try:
                                restarts = int(restart_str) if restart_str.isdigit() else 0
                            except ValueError:
                                restarts = 0

                        # Extract memory (column 11)
                        memory = "N/A"
                        if len(parts) > 11:
                            mem_col = parts[11].strip().lower()
                            if "mb" in mem_col:
                                # Extract the memory value (e.g., "11.6mb" -> "11.6mb")
                                mem_match = re.search(r'([\d.]+)\s*([a-z]+)', mem_col)
                                if mem_match:
                                    memory = f"{mem_match.group(1)}{mem_match.group(2)}"
                            elif "gb" in mem_col:
                                mem_match = re.search(r'([\d.]+)\s*([a-z]+)', mem_col)
                                if mem_match:
                                    memory = f"{mem_match.group(1)}{mem_match.group(2)}"
                            elif "b" in mem_col:  # bytes
                                memory = mem_col

                        # Add to processes dictionary
                        if name and name != "id":
                            processes[name] = {
                                "restarts": restarts,
                                "memory": memory,
                                "status": status
                            }
                    except (IndexError, ValueError) as e:
                        # Skip lines that don't parse correctly
                        continue

        return processes

    def check_cloud(self) -> None:
        """Check Cloud VM health."""
        print("Checking Cloud VM...")

        # PM2 status (text format for parsing)
        pm2_output = self.run_command(["pm2", "status"], ssh=True)
        if pm2_output and not pm2_output.startswith("Error"):
            self.report["cloud"]["pm2"] = self.parse_pm2_status(pm2_output)
        else:
            print(f"  Warning: Could not connect to Cloud VM")
            self.report["cloud"]["pm2"] = {}

        # Count online/stopped
        cloud_processes = self.report["cloud"]["pm2"]
        if cloud_processes:
            online = sum(1 for p in cloud_processes.values() if p.get("status") == "online")
            stopped = sum(1 for p in cloud_processes.values() if p.get("status") == "stopped")
            high_restarts = sum(1 for p in cloud_processes.values() if isinstance(p.get("restarts"), int) and p["restarts"] > 10)

            self.report["cloud"]["summary"] = {
                "total": len(cloud_processes),
                "online": online,
                "stopped": stopped,
                "high_restarts": high_restarts
            }
        else:
            self.report["cloud"]["summary"] = {"total": 0, "online": 0, "stopped": 0, "high_restarts": 0}

    def check_local(self) -> None:
        """Check Local machine health."""
        print("Checking Local machine...")

        # PM2 status (text format for parsing)
        pm2_output = self.run_command(["pm2", "status"], ssh=False)
        if pm2_output and not pm2_output.startswith("Error"):
            self.report["local"]["pm2"] = self.parse_pm2_status(pm2_output)
        else:
            print(f"  Warning: Could not get PM2 status")
            self.report["local"]["pm2"] = {}

        # Count online/stopped
        local_processes = self.report["local"]["pm2"]
        if local_processes:
            online = sum(1 for p in local_processes.values() if p.get("status") == "online")
            stopped = sum(1 for p in local_processes.values() if p.get("status") == "stopped")
            high_restarts = sum(1 for p in local_processes.values() if isinstance(p.get("restarts"), int) and p["restarts"] > 10)

            self.report["local"]["summary"] = {
                "total": len(local_processes),
                "online": online,
                "stopped": stopped,
                "high_restarts": high_restarts
            }
        else:
            self.report["local"]["summary"] = {"total": 0, "online": 0, "stopped": 0, "high_restarts": 0}

    def check_git_sync(self) -> None:
        """Check git sync status."""
        print("Checking git sync...")

        # Local git status
        git_status = self.run_command(["git", "status", "--short"], ssh=False)
        self.report["git_sync"]["local_changes"] = len([l for l in git_status.split('\n') if l.strip()])

        # Latest commits
        git_log = self.run_command(["git", "log", "--oneline", "-3"], ssh=False)
        self.report["git_sync"]["recent_commits"] = git_log.strip().split('\n')

    def generate_recommendations(self) -> None:
        """Generate system improvement recommendations."""
        print("Generating recommendations...")

        # Cloud recommendations
        cloud_procs = self.report["cloud"]["pm2"]
        for name, proc in cloud_procs.items():
            if isinstance(proc.get("restarts"), int) and proc["restarts"] > 10:
                self.report["recommendations"].append({
                    "type": "warning",
                    "target": f"cloud:{name}",
                    "message": f"{name} has {proc['restarts']} restarts"
                })
            if "mb" in proc.get("memory", ""):
                mem_val = float(proc["memory"].replace("mb", ""))
                if mem_val > 100:
                    self.report["recommendations"].append({
                        "type": "warning",
                        "target": f"cloud:{name}",
                        "message": f"{name} using {proc['memory']} memory"
                    })

        # Local recommendations
        local_procs = self.report["local"]["pm2"]
        for name, proc in local_procs.items():
            if isinstance(proc.get("restarts"), int) and proc["restarts"] > 10:
                self.report["recommendations"].append({
                    "type": "warning",
                    "target": f"local:{name}",
                    "message": f"{name} has {proc['restarts']} restarts"
                })

        # Git sync recommendations
        if self.report["git_sync"]["local_changes"] > 50:
            self.report["recommendations"].append({
                "type": "info",
                "target": "git",
                "message": f"{self.report['git_sync']['local_changes']} uncommitted changes - consider committing"
            })

    def generate_report(self) -> str:
        """Generate formatted health report."""
        report = []
        report.append("=" * 70)
        report.append("AI EMPLOYEE SYSTEM HEALTH REPORT")
        report.append(f"Generated: {self.report['timestamp']}")
        report.append("=" * 70)

        # Cloud Status
        report.append("\n[CLOUD] CLOUD VM (143.244.143.143)")
        report.append("-" * 70)
        cloud_summary = self.report["cloud"]["summary"]
        report.append(f"Processes: {cloud_summary['online']}/{cloud_summary['total']} online")
        report.append(f"High restarts: {cloud_summary['high_restarts']}")
        report.append("\nProcess Details:")
        for name, proc in sorted(self.report["cloud"]["pm2"].items()):
            restarts = proc.get("restarts", "N/A")
            memory = proc.get("memory", "N/A")
            status = proc.get("status", "unknown")
            status_emoji = "[OK]" if status == "online" else "[STOPPED]"
            report.append(f"  {status_emoji} {name:25} | {str(restarts):>10} restarts | {memory:>8}")

        # Local Status
        report.append("\n[LOCAL] LOCAL MACHINE")
        report.append("-" * 70)
        local_summary = self.report["local"]["summary"]
        report.append(f"Processes: {local_summary['online']}/{local_summary['total']} online")
        report.append(f"High restarts: {local_summary['high_restarts']}")
        report.append("\nProcess Details:")
        for name, proc in sorted(self.report["local"]["pm2"].items()):
            restarts = proc.get("restarts", "N/A")
            memory = proc.get("memory", "N/A")
            status = proc.get("status", "unknown")
            status_emoji = "[OK]" if status == "online" else "[STOPPED]"
            report.append(f"  {status_emoji} {name:25} | {str(restarts):>10} restarts | {memory:>8}")

        # Git Sync Status
        report.append("\n[GIT] GIT SYNC")
        report.append("-" * 70)
        report.append(f"Uncommitted changes: {self.report['git_sync']['local_changes']}")
        report.append("\nRecent commits:")
        for commit in self.report["git_sync"]["recent_commits"]:
            report.append(f"  {commit}")

        # Recommendations
        if self.report["recommendations"]:
            report.append("\n[!]  RECOMMENDATIONS")
            report.append("-" * 70)
            for rec in self.report["recommendations"]:
                emoji = {"warning": "[!]", "info": "ℹ️", "error": "❌"}.get(rec["type"], "•")
                report.append(f"  {emoji} [{rec['target']}] {rec['message']}")
        else:
            report.append("\n[OK] No recommendations - System healthy!")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def save_report(self, output: str = None) -> str:
        """Generate and save health report."""
        if not output:
            output = self.vault_path / "Briefings" / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        report_text = self.generate_report()

        # Save to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text)

        print(f"\n[OK] Health report saved to: {output_path}")
        return report_text


def main():
    parser = argparse.ArgumentParser(description="Generate AI Employee system health report")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    generator = HealthReportGenerator(args.vault)

    # Check all systems
    generator.check_cloud()
    generator.check_local()
    generator.check_git_sync()
    generator.generate_recommendations()

    # Generate report
    if args.json:
        print(json.dumps(generator.report, indent=2))
    else:
        report = generator.generate_report()
        print(report)
        generator.save_report(args.output)


if __name__ == "__main__":
    main()
