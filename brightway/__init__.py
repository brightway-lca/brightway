__all__ = [
    'projects',
]

__version__ = (3, 0, "dev")


config = {}

from .base_dir import get_base_directories

BASE_DIR, BASE_LOG_DIR = get_base_directories()

from .filesystem import create_base_dir
create_base_dir()

from .projects import Project, ProjectManager
projects = ProjectManager()
