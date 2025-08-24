"""
Centralized Django initialization for the AI workflow.
This module handles Django setup in a clean, reusable way.
"""
import os
import sys
import django
from pathlib import Path
from typing import Optional


class DjangoInitializer:
    """Handles Django environment setup and initialization."""
    
    _initialized = False
    _project_root: Optional[Path] = None
    
    @classmethod
    def get_project_root(cls) -> Path:
        """Get the Django project root directory."""
        if cls._project_root is None:
            # Navigate up from current file to find project root
            current_file = Path(__file__)
            cls._project_root = current_file.parent.parent.parent.parent.parent
        return cls._project_root
    
    @classmethod
    def setup_django(cls, settings_module: str = 'graduation_backend.settings') -> None:
        """
        Initialize Django environment if not already configured.
        
        Args:
            settings_module: The Django settings module to use
        """
        if cls._initialized:
            return
        
        # Set Django settings module if not already set
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
        
        # Add project root to Python path if not already there
        project_root = cls.get_project_root()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Initialize Django
        try:
            django.setup()
            cls._initialized = True
            print(f"✓ Django initialized successfully with settings: {settings_module}")
        except Exception as e:
            print(f"✗ Failed to initialize Django: {e}")
            raise
    
    @classmethod
    def ensure_django_ready(cls) -> None:
        """Ensure Django is ready, initializing if necessary."""
        if not cls._initialized:
            cls.setup_django()
    
    @classmethod
    def reset(cls) -> None:
        """Reset the initialization state (useful for testing)."""
        cls._initialized = False
        cls._project_root = None


def setup_django(settings_module: str = 'graduation_backend.settings') -> None:
    """
    Convenience function for backward compatibility.
    Use DjangoInitializer.setup_django() for more control.
    """
    DjangoInitializer.setup_django(settings_module)


def ensure_django_ready() -> None:
    """
    Convenience function to ensure Django is ready.
    """
    DjangoInitializer.ensure_django_ready()


# Don't auto-initialize - let the calling code control when Django is set up
# This prevents the "populate() isn't reentrant" error
