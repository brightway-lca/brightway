__all__ = [
    'projects',
    'Project',
    'bwtest',
]

__version__ = (3, 0, "dev")


from .base_dir import get_base_directories
_BASE_DIR, _BASE_LOG_DIR = get_base_directories()

from .peewee import SubstitutableDatabase
from .projects import Project, ProjectManager

_BASE_DIR.mkdir(parents=True, exist_ok=True)
project_database = SubstitutableDatabase(_BASE_DIR / "projects.db", [Project])

projects = ProjectManager(_BASE_DIR, _BASE_LOG_DIR)

from .testing import bwtest
