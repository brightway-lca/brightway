# -*- coding: utf-8 -*-
from . import backend_mapping
from .errors import MissingBackend
from .filesystem import safe_filename, get_dir_size, create_dir
from .peewee import JSONField
from peewee import Model, TextField, BlobField, BooleanField, DoesNotExist
import appdirs
import collections
import os
import shutil
import warnings


class Project(Model):
    data = JSONField(default={})
    backends = JSONField(default=[])
    directory = TextField()
    name = TextField(index=True, unique=True)
    default = BooleanField(default=False)
    enabled = BooleanField(default=True)

    def __str__(self):
        return "Project: {}".format(self.name)

    __repr__ = lambda x: str(x)

    def __lt__(self, other):
        # Allow ordering
        if not isinstance(other, ProjectDataset):
            raise TypeError
        else:
            return self.name.lower() < other.name.lower()

    def backends_resolved(self):
        for label in (self.backends or []):
            yield backend_mapping[label]


class ProjectManager(collections.abc.Iterable):
    def __init__(self, base_dir, base_log_dir):
        self.base_dir = base_dir
        self.base_log_dir = base_log_dir
        self.create_base_dirs()
        try:
            self.current = Project.get(Project.default == True)
        except DoesNotExist:
            self.current = None

    def create_base_dirs(self):
        """Create directory for storing data on projects.

        Most projects will be subdirectories.

        Returns a directory path."""
        create_dir(self.base_dir)
        create_dir(self.base_log_dir)
        if not os.access(self.base_dir, os.W_OK):
            WARNING = ("Brightway directory exists, but is read-only. "
                        "Please fix this and restart.")
            warnings.warn(WARNING)

    def __iter__(self):
        for project_ds in Project.select().where(Project.enabled == True):
            yield project_ds

    def __contains__(self, name):
        return Project.select().where(Project.name == name).count() > 0

    def __len__(self):
        return Project.select().where(Project.enabled == True).count()

    def __repr__(self):
        if len(self) > 20:
            return ("Brightway projects manager with {} objects, including:"
                    "{}\nUse `sorted(projects)` to get full list, "
                    "`projects.report()` to get\n\ta report on all projects.").format(
                len(self),
                "".join(["\n\t{}".format(x) for x in sorted([x.name for x in self])[:10]])
            )
        else:
            return ("Brightway projects manager with {} objects:{}"
                    "\nUse `projects.report()` to get a report on all projects.").format(
                len(self),
                "".join(["\n\t{}".format(x) for x in sorted([x.name for x in self])])
            )

    @property
    def dir(self):
        return self.current.directory if self.current else None

    def select(self, name):
        if self.current:
            self.deactivate()
        self.current = Project.get(name=name)
        self.activate()

    def activate(self):
        """Activate the current project with its backends"""
        for backend in self.current.backends_resolved():
            backend.activate_project(self.current)

    def deactivate(self):
        """Deactivate the current project with its backends"""
        for backend in self.current.backends_resolved():
            backend.deactivate_project(self.current)
        self.current = None

    def create(self, name, backends=('default',), switch=True, default=False, **kwargs):
        if name in self:
            print("This project already exists; use "
                  "`projects.select({})` to switch.".format(name))

        if backends is None and 'default' not in backend_mapping:
            raise MissingBackend("No `default` backend available; "
                                  "Must specify a project backend.")

        dirpath = self.base_dir / safe_filename(name)
        dirpath.mkdir()
        if default:
            # Set all other projects to non-default
            Project.update(default=False).execute()
        obj = Project.create(
            name=name,
            directory=dirpath,
            data=kwargs,
            backends=backends,
            default=default,
        )

        for backend in obj.backends_resolved():
            if getattr(backend, "__brightway_common_api__"):
                backend.create_project(obj)

        if switch:
            self.select(name)

    # def copy_project(self, new_name, switch=True, default=False):
    # Should be defined by backend
    #     """Copy current project to a new project named ``new_name``. If ``switch``, switch to new project."""
    #     if new_name in self:
    #         raise ValueError("Project {} already exists".format(new_name))
    #     fp = os.path.join(self._base_data_dir, safe_filename(new_name))
    #     if os.path.exists(fp):
    #         raise ValueError("Project directory already exists")
    #     project_data = ProjectDataset.select(ProjectDataset.name == self.current).get().data
    #     ProjectDataset.create(data=project_data, name=new_name)
    #     shutil.copytree(self.dir, fp, ignore=lambda x, y: ["write-lock"])
    #     create_dir(os.path.join(
    #         self._base_logs_dir,
    #         safe_filename(new_name)
    #     ))
    #     if switch:
    #         self.set_current(new_name)

    def delete_project(self, name):
        """Delete project ``name``.

        Set the ``.enabled`` to ``False`` to exclude this project instead of deleting it."""
        if name == self.current:
            self.deactivate()

        try:
            obj = Project.get(Project.name == name)
        except DoesNotExist:
            raise ValueError("{} is not a project".format(name))

        for backend in obj.backends_resolved():
            backend.delete_project(obj)

        obj.delete_instance()
        shutil.rmtree(directory)

    # def purge_deleted_directories(self):
    #     """Delete project directories for projects which are no longer registered.

    #     Returns number of directories deleted."""
    #     registered = {safe_filename(obj.name) for obj in self}
    #     bad_directories = [os.path.join(self._base_data_dir, dirname)
    #                        for dirname in os.listdir(self._base_data_dir)
    #                        if os.path.isdir(os.path.join(self._base_data_dir, dirname))
    #                        and dirname not in registered]

    #     for fp in bad_directories:
    #         shutil.rmtree(fp)

    #     return len(bad_directories)

    def report(self):
        """Give a report on current projects, backend, and directory sizes.

        Returns tuples of ``(project name, backend name, and directory size (GB))``."""
        return sorted([
            (x.name, x.backends, get_dir_size(x.directory)) for x in self
        ])

    # def use_temp_directory(self):
    #     """Point the ProjectManager towards a temporary directory instead of `user_data_dir`.

    #     Used exclusively for tests."""
    #     if not self._is_temp_dir:
    #         self._orig_base_data_dir = self._base_data_dir
    #         self._orig_base_logs_dir = self._base_logs_dir
    #     temp_dir = tempfile.mkdtemp()
    #     self._base_data_dir = os.path.join(temp_dir, "data")
    #     self._base_logs_dir = os.path.join(temp_dir, "logs")
    #     self.db.change_path(':memory:')
    #     self.select("tests-default")
    #     self._is_temp_dir = True
    #     return temp_dir
