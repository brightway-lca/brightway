from .version import version as __version__

__all__ = [
    "backend_mapping",
    "JSONField",
    "PathField",
    "Project",
    "projects",
    "TupleField",
]


from .peewee import JSONField, PathField, SubstitutableDatabase, TupleField

backend_mapping = {}

from .base_dir import get_base_directories

_BASE_DIR, _BASE_LOG_DIR = get_base_directories()

from .projects import Project, ProjectManager

_BASE_DIR.mkdir(parents=True, exist_ok=True)
project_database = SubstitutableDatabase(_BASE_DIR / "projects.db", [Project])

projects = ProjectManager(_BASE_DIR, _BASE_LOG_DIR)
