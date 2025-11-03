"""
Audit logging for security events
Tracks authentication, file access, and security-related events
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of security events to log"""
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_FAILED = "auth_failed"
    FILE_UPLOAD = "file_upload"
    FILE_ACCESS = "file_access"
    FILE_DELETE = "file_delete"
    API_ACCESS = "api_access"
    SECURITY_ALERT = "security_alert"
    CONFIG_CHANGE = "config_change"
    KEY_ROTATION = "key_rotation"


class AuditLogger:
    """
    Security audit logger for tracking critical events
    """
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize audit logger
        
        Args:
            log_file: Path to audit log file (default: logs/audit.log)
        """
        if log_file is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "audit.log"
        
        self.log_file = log_file
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup file logger for audit events"""
        # Create dedicated audit logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        
        # JSON format for easy parsing
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def log_event(
        self,
        event_type: EventType,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        ip_address: Optional[str] = None
    ):
        """
        Log a security event
        
        Args:
            event_type: Type of event
            user_id: User identifier
            details: Additional event details
            success: Whether event was successful
            ip_address: Client IP address
        """
        event_data = {
            "event_type": event_type.value,
            "user_id": user_id or "anonymous",
            "success": success,
            "ip_address": ip_address or "unknown",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if details:
            event_data["details"] = details
        
        # Log to file
        self.logger.info(json.dumps(event_data))
        
        # Also log to console for monitoring
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUDIT [{status}] {event_type.value} - User: {user_id}")
    
    def log_login(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log login attempt"""
        event_type = EventType.AUTH_LOGIN if success else EventType.AUTH_FAILED
        self.log_event(event_type, user_id, details, success, ip_address)
    
    def log_logout(
        self,
        user_id: str,
        ip_address: Optional[str] = None
    ):
        """Log logout event"""
        self.log_event(EventType.AUTH_LOGOUT, user_id, None, True, ip_address)
    
    def log_file_upload(
        self,
        user_id: str,
        filename: str,
        file_size: int,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """Log file upload"""
        details = {
            "filename": filename,
            "file_size": file_size
        }
        self.log_event(EventType.FILE_UPLOAD, user_id, details, success, ip_address)
    
    def log_file_access(
        self,
        user_id: str,
        filename: str,
        access_type: str,
        ip_address: Optional[str] = None
    ):
        """Log file access"""
        details = {
            "filename": filename,
            "access_type": access_type
        }
        self.log_event(EventType.FILE_ACCESS, user_id, details, True, ip_address)
    
    def log_security_alert(
        self,
        alert_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log security alert"""
        details = {
            "alert_type": alert_type,
            "description": description
        }
        self.log_event(EventType.SECURITY_ALERT, user_id, details, False, ip_address)
    
    def log_api_access(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        status_code: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log API access"""
        details = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code
        }
        success = status_code is None or 200 <= status_code < 400
        self.log_event(EventType.API_ACCESS, user_id, details, success, ip_address)
    
    def get_recent_events(
        self,
        event_type: Optional[EventType] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Get recent audit events
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user
            limit: Maximum number of events
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            if not self.log_file.exists():
                return events
            
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        
                        # Filter by event type
                        if event_type and event.get('event_type') != event_type.value:
                            continue
                        
                        # Filter by user
                        if user_id and event.get('user_id') != user_id:
                            continue
                        
                        events.append(event)
                        
                        if len(events) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
        
        return events[-limit:]  # Return most recent
    
    def get_failed_logins(self, hours: int = 24) -> list:
        """
        Get failed login attempts in last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of failed login events
        """
        events = self.get_recent_events(event_type=EventType.AUTH_FAILED)
        
        # Filter by time
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        
        recent_events = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['timestamp']).timestamp()
                if event_time >= cutoff:
                    recent_events.append(event)
            except (KeyError, ValueError):
                continue
        
        return recent_events
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> list:
        """
        Get activity for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum events to return
            
        Returns:
            List of user events
        """
        return self.get_recent_events(user_id=user_id, limit=limit)


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
