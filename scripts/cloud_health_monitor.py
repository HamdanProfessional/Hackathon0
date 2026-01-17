#!/usr/bin/env python3
"""
Cloud Health Monitor for Platinum Tier.

Monitors cloud VM health and reports status to Updates/ folder
for local agent to merge into Dashboard.md (single writer rule).

Runs every 5 minutes and reports:
- CPU, Memory, Disk usage
- PM2 process status
- System uptime
- Network connectivity
"""

import json
import os
import sys
import psutil
from datetime import datetime
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CloudHealthMonitor:
    """
    Monitors cloud VM health and writes status updates to vault.
    """

    def __init__(self, vault_path: str, interval: int = 300):
        """
        Initialize health monitor.

        Args:
            vault_path: Path to the vault
            interval: Check interval in seconds (default: 300 = 5 minutes)
        """
        self.vault_path = Path(vault_path)
        self.updates_path = self.vault_path / 'Updates'
        self.updates_path.mkdir(parents=True, exist_ok=True)
        self.interval = interval

    def get_system_health(self) -> dict:
        """Collect system health metrics."""

        health = {
            'timestamp': datetime.now().isoformat(),
            'hostname': os.uname().nodename,
            'system': {
                'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1)
            },
            'memory': {
                'total_gb': psutil.virtual_memory().total / (1024**3),
                'available_gb': psutil.virtual_memory().available / (1024**3),
                'percent': psutil.virtual_memory().percent,
                'used_gb': psutil.virtual_memory().used / (1024**3)
            },
            'disk': {
                'total_gb': psutil.disk_usage('/').total / (1024**3),
                'used_gb': psutil.disk_usage('/').used / (1024**3),
                'free_gb': psutil.disk_usage('/').free / (1024**3),
                'percent': psutil.disk_usage('/').percent
            },
            'network': self._get_network_info(),
            'processes': self._get_pm2_status()
        }

        return health

    def _get_network_info(self) -> dict:
        """Get network information."""

        network = {
            'connections': len(psutil.net_connections()),
            'interfaces': {}
        }

        # Get interface stats
        stats = psutil.net_io_counters(pernic=True)
        for interface, counters in stats.items():
            network['interfaces'][interface] = {
                'bytes_sent': counters.bytes_sent,
                'bytes_recv': counters.bytes_recv,
                'packets_sent': counters.packets_sent,
                'packets_recv': counters.packets_recv
            }

        return network

    def _get_pm2_status(self) -> dict:
        """Get PM2 process status."""

        processes = {}

        try:
            result = os.popen('pm2 jlist').read()
            pm2_processes = json.loads(result)

            for proc in pm2_processes:
                name = proc['name']
                pm2_env = proc.get('pm2_env', {})
                monit = proc.get('monit', {})

                processes[name] = {
                    'status': pm2_env.get('status', 'unknown'),
                    'cpu': monit.get('cpu', 0),
                    'memory_mb': monit.get('memory', 0) / (1024**2),
                    'uptime': pm2_env.get('pm_uptime', 0),
                    'restarts': pm2_env.get('restart_time', 0),
                    'pid': proc.get('pid', 0)
                }

        except Exception as e:
            logger.error(f"Failed to get PM2 status: {e}")
            processes['error'] = str(e)

        return processes

    def write_health_update(self, health: dict):
        """
        Write health update to Updates/ folder.

        Args:
            health: Health status dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        update_file = self.updates_path / f'cloud_health_{timestamp}.json'

        with open(update_file, 'w', encoding='utf-8') as f:
            json.dump(health, f, indent=2)

        logger.info(f"Health update written to {update_file}")

    def check_health_alerts(self, health: dict) -> list:
        """
        Check for health alerts and return list of alerts.

        Args:
            health: Health status dictionary

        Returns:
            List of alert messages
        """
        alerts = []

        # CPU alert
        if health['system']['cpu_percent'] > 80:
            alerts.append(f"HIGH CPU: {health['system']['cpu_percent']:.1f}%")

        # Memory alert
        if health['memory']['percent'] > 80:
            alerts.append(f"HIGH MEMORY: {health['memory']['percent']:.1f}%")

        # Disk alert
        if health['disk']['percent'] > 80:
            alerts.append(f"HIGH DISK: {health['disk']['percent']:.1f}%")

        # Check for failed processes
        for name, proc in health['processes'].items():
            if proc.get('status') == 'errored':
                alerts.append(f"PROCESS ERRORED: {name}")
            elif proc.get('status') == 'stopped':
                alerts.append(f"PROCESS STOPPED: {name}")

        return alerts

    def run_once(self):
        """Run a single health check."""
        try:
            health = self.get_system_health()
            alerts = self.check_health_alerts(health)

            if alerts:
                health['alerts'] = alerts
                logger.warning(f"Health alerts: {alerts}")

            self.write_health_update(health)

            # Log summary
            logger.info(
                f"Health: CPU {health['system']['cpu_percent']:.1f}% | "
                f"Memory {health['memory']['percent']:.1f}% | "
                f"Disk {health['disk']['percent']:.1f}%"
            )

            return health

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return None

    def run_continuous(self):
        """Run continuous health monitoring."""
        logger.info(f"Starting health monitor (interval: {self}s)")

        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                logger.info("Health monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

            # Wait for next check
            import time
            time.sleep(self.interval)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Cloud health monitor")
    parser.add_argument(
        '--vault',
        default=os.getenv('VAULT_PATH', 'AI_Employee_Vault'),
        help='Path to vault'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )

    args = parser.parse_args()

    monitor = CloudHealthMonitor(args.vault, args.interval)

    if args.once:
        health = monitor.run_once()
        if health:
            print(json.dumps(health, indent=2))
    else:
        monitor.run_continuous()


if __name__ == '__main__':
    main()
