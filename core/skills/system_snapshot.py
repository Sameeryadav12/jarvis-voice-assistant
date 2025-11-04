"""
System Snapshot Skills

Provides comprehensive system state summary:
- Resource usage overview
- Network status
- Application state
- System health metrics
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from loguru import logger
import psutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


@dataclass
class SystemSnapshot:
    """Comprehensive system snapshot data."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage: Dict[str, Any]
    network_interfaces: List[Dict[str, Any]]
    running_apps: List[Dict[str, Any]]
    battery_info: Optional[Dict[str, Any]]
    system_info: Dict[str, Any]


class SystemSnapshotSkills:
    """
    System snapshot skills for comprehensive system state overview.
    
    Features:
    - CPU and memory usage
    - Disk space
    - Network status
    - Running applications
    - Battery status (if available)
    - System information
    """
    
    def __init__(self):
        """Initialize system snapshot skills."""
        logger.info("SystemSnapshotSkills initialized")
    
    def get_snapshot(self) -> SystemSnapshot:
        """
        Get comprehensive system snapshot.
        
        Returns:
            SystemSnapshot object
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        
        # Disk usage
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "total_gb": usage.total / (1024 ** 3),
                    "used_gb": usage.used / (1024 ** 3),
                    "free_gb": usage.free / (1024 ** 3),
                    "percent": (usage.used / usage.total) * 100,
                }
            except PermissionError:
                continue
        
        # Network interfaces
        network_interfaces = []
        net_io = psutil.net_io_counters(pernic=True)
        net_if_addrs = psutil.net_if_addrs()
        
        for interface_name, addresses in net_if_addrs.items():
            interface_info = {
                "name": interface_name,
                "addresses": [],
                "bytes_sent": 0,
                "bytes_recv": 0,
            }
            
            for addr in addresses:
                interface_info["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask if hasattr(addr, 'netmask') else None,
                })
            
            if interface_name in net_io:
                interface_info["bytes_sent"] = net_io[interface_name].bytes_sent
                interface_info["bytes_recv"] = net_io[interface_name].bytes_recv
            
            # Only include active interfaces
            if interface_info["addresses"]:
                network_interfaces.append(interface_info)
        
        # Running applications
        running_apps = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                proc_info = proc.info
                proc_info['memory_mb'] = proc.memory_info().rss / (1024 ** 2)
                running_apps.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by memory usage
        running_apps.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        running_apps = running_apps[:20]  # Top 20
        
        # Battery info (if available)
        battery_info = None
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_info = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "time_left": battery.secsleft if battery.secsleft != -1 else None,
                }
        except Exception:
            pass  # Battery not available
        
        # System info
        system_info = {
            "platform": sys.platform,
            "cpu_count": cpu_count,
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()),
            "users": [u.name for u in psutil.users()],
        }
        
        snapshot = SystemSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            disk_usage=disk_usage,
            network_interfaces=network_interfaces,
            running_apps=running_apps,
            battery_info=battery_info,
            system_info=system_info,
        )
        
        return snapshot
    
    def get_snapshot_summary(self) -> SkillResult:
        """
        Get human-readable system snapshot summary.
        
        Returns:
            Skill result with formatted summary
        """
        snapshot = self.get_snapshot()
        
        # Build summary message
        lines = []
        lines.append("System Snapshot:")
        lines.append(f"  CPU: {snapshot.cpu_percent:.1f}%")
        lines.append(f"  Memory: {snapshot.memory_used_gb:.1f}GB / {snapshot.memory_total_gb:.1f}GB ({snapshot.memory_percent:.1f}%)")
        
        # Disk usage
        for device, usage in list(snapshot.disk_usage.items())[:3]:  # Top 3
            lines.append(f"  Disk {device}: {usage['used_gb']:.1f}GB / {usage['total_gb']:.1f}GB ({usage['percent']:.1f}%)")
        
        # Network
        active_interfaces = [ni for ni in snapshot.network_interfaces if ni['bytes_sent'] > 0 or ni['bytes_recv'] > 0]
        if active_interfaces:
            lines.append(f"  Network: {len(active_interfaces)} active interface(s)")
        
        # Battery
        if snapshot.battery_info:
            batt = snapshot.battery_info
            status = "plugged in" if batt['power_plugged'] else "on battery"
            lines.append(f"  Battery: {batt['percent']:.0f}% ({status})")
        
        # Top apps
        if snapshot.running_apps:
            top_app = snapshot.running_apps[0]
            lines.append(f"  Top app: {top_app.get('name', 'Unknown')} ({top_app.get('memory_percent', 0):.1f}% memory)")
        
        message = "\n".join(lines)
        
        return SkillResult(
            success=True,
            message=message,
            data=snapshot.__dict__
        )
    
    def get_resource_usage(self) -> SkillResult:
        """
        Get detailed resource usage.
        
        Returns:
            Skill result with resource usage
        """
        snapshot = self.get_snapshot()
        
        message = (
            f"Resource Usage:\n"
            f"  CPU: {snapshot.cpu_percent:.1f}%\n"
            f"  Memory: {snapshot.memory_percent:.1f}% "
            f"({snapshot.memory_used_gb:.1f}GB / {snapshot.memory_total_gb:.1f}GB)\n"
        )
        
        # Add disk usage
        for device, usage in snapshot.disk_usage.items():
            message += f"  {device}: {usage['percent']:.1f}% used\n"
        
        return SkillResult(
            success=True,
            message=message.strip(),
            data={
                "cpu_percent": snapshot.cpu_percent,
                "memory_percent": snapshot.memory_percent,
                "memory_used_gb": snapshot.memory_used_gb,
                "memory_total_gb": snapshot.memory_total_gb,
                "disk_usage": snapshot.disk_usage,
            }
        )
    
    def get_network_status(self) -> SkillResult:
        """
        Get network status summary.
        
        Returns:
            Skill result with network status
        """
        snapshot = self.get_snapshot()
        
        active_interfaces = [
            ni for ni in snapshot.network_interfaces
            if ni['bytes_sent'] > 0 or ni['bytes_recv'] > 0
        ]
        
        if not active_interfaces:
            return SkillResult(
                success=True,
                message="No active network interfaces",
                data={"interfaces": []}
            )
        
        lines = ["Network Status:"]
        for interface in active_interfaces[:5]:  # Top 5
            sent_mb = interface['bytes_sent'] / (1024 ** 2)
            recv_mb = interface['bytes_recv'] / (1024 ** 2)
            lines.append(
                f"  {interface['name']}: "
                f"Sent: {sent_mb:.1f}MB, Received: {recv_mb:.1f}MB"
            )
        
        message = "\n".join(lines)
        
        return SkillResult(
            success=True,
            message=message,
            data={"interfaces": active_interfaces}
        )
    
    def get_running_apps(self, top_n: int = 10) -> SkillResult:
        """
        Get top running applications by memory usage.
        
        Args:
            top_n: Number of apps to return
            
        Returns:
            Skill result with app list
        """
        snapshot = self.get_snapshot()
        
        top_apps = snapshot.running_apps[:top_n]
        
        lines = [f"Top {top_n} applications by memory:"]
        for i, app in enumerate(top_apps, 1):
            name = app.get('name', 'Unknown')
            memory_percent = app.get('memory_percent', 0)
            memory_mb = app.get('memory_mb', 0)
            lines.append(f"  {i}. {name}: {memory_percent:.1f}% ({memory_mb:.0f}MB)")
        
        message = "\n".join(lines)
        
        return SkillResult(
            success=True,
            message=message,
            data={"apps": top_apps}
        )
    
    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle system snapshot intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        if intent.type == IntentType.GET_SYSTEM_INFO:
            return self.get_snapshot_summary()
        
        # Map other intents as needed
        return SkillResult(
            success=False,
            message=f"Unknown snapshot intent: {intent.type.value}"
        )

