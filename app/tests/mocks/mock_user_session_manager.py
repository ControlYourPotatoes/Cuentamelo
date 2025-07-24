"""
Mock User Session Manager for testing.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from app.ports.frontend_port import UserSessionManager, UserSession


class MockUserSessionManager(UserSessionManager):
    """Mock user session manager for testing"""
    
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
    
    async def create_session(self, user_id: Optional[str] = None) -> UserSession:
        """Create a mock session"""
        session_id = f"mock_session_{len(self.sessions) + 1}"
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            permissions=["read", "write"],
            preferences={},
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc)
        )
        self.sessions[session_id] = session
        return session
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a mock session"""
        return self.sessions.get(session_id)
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session activity"""
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.now(timezone.utc)
            return True
        return False
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False 