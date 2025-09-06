from .auth import auth_bp
from .user import user_bp
from .learning import learning_bp
from .quiz import quiz_bp
from .community import community_bp

__all__ = ['auth_bp', 'user_bp', 'learning_bp', 'quiz_bp', 'community_bp']