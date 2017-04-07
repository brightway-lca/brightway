__all__ = [
    'projects',
    'backend_mapping',
]

__version__ = (3, 0, "dev")

backend_mapping = {}
try:
    from bw_default_backend import config as default_config
    backend_mapping['default'] = default_config
except ImportError:
    pass

from .filesystem import create_base_project_dir
base_dir = create_base_project_dir()

from .projects import Project, ProjectManager
projects = ProjectManager(base_dir)
