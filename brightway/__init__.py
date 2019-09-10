__all__ = [
    'projects',
    'Project',
    'backend_mapping',
]

__version__ = (3, 0, "dev")


backend_mapping = {}
try:
    from bw_default_backend import Config as DefaultBackend
    backend_mapping['default'] = DefaultBackend()
except ImportError:
    pass


from .base_dir import get_base_directories
_BASE_DIR, _BASE_LOG_DIR = get_base_directories()

from .peewee import SubstitutableDatabase
from .projects import Project, ProjectManager

_BASE_DIR.mkdir(parents=True, exist_ok=True)
project_database = SubstitutableDatabase(_BASE_DIR / "projects.db", [Project])

projects = ProjectManager(_BASE_DIR, _BASE_LOG_DIR)
