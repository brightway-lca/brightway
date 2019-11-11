# -*- coding: utf-8 -*-
from . import backend_mapping
from .errors import MissingBackend
from .filesystem import safe_filename, get_dir_size, create_dir
from .peewee import JSONField, PathField
from peewee import Model, TextField, BooleanField, DoesNotExist
import collections
import os
import shutil
import warnings


class Project(Model):
    data = JSONField(default={})
    backends = JSONField(default=[])
    directory = PathField()
    name = TextField(index=True, unique=True)
    default = BooleanField(default=False)
    enabled = BooleanField(default=True)

    def __str__(self):
        return "Project: {}".format(self.name)

    __repr__ = lambda x: str(x)

    def __lt__(self, other):
        # Allow ordering
        if not isinstance(other, Project):
            raise TypeError
        else:
            return self.name.lower() < other.name.lower()

    def backends_resolved(self):
        for label in self.backends or []:
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
            WARNING = (
                "Brightway directory exists, but is read-only. "
                "Please fix this and restart."
            )
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
            return (
                "Brightway projects manager with {} objects, including:"
                "{}\nUse `sorted(projects)` to get full list, "
                "`projects.report()` to get\n\ta report on all projects."
            ).format(
                len(self),
                "".join(
                    ["\n\t{}".format(x) for x in sorted([x.name for x in self])[:10]]
                ),
            )
        else:
            return (
                "Brightway projects manager with {} objects:{}"
                "\nUse `projects.report()` to get a report on all projects."
            ).format(
                len(self),
                "".join(["\n\t{}".format(x) for x in sorted([x.name for x in self])]),
            )

    @property
    def dir(self):
        return self.current.directory if self.current else None

    def select(self, name):
        if name not in self:
            raise ValueError("Project f{name} doesn't exist")
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
            backend.deactivate_project()
        self.current = None

    def create_project(
        self, name, backends=("default",), switch=True, default=False, **kwargs
    ):
        if name in self:
            print(
                "This project already exists; use "
                "`projects.select('{}'')` to switch.".format(name)
            )
            return

        if backends is None and "default" not in backend_mapping:
            raise MissingBackend(
                "No `default` backend available; " "Must specify a project backend."
            )
        for backend in backends:
            if backend not in backend_mapping:
                raise MissingBackend(f"Backend {backend} missing")

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
            if getattr(backend, "__brightway_common_api__", None):
                backend.create_project(obj, **kwargs)

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

    def delete_project(self, project):
        """Delete project ``project``.

        ``project`` can be a name (sstr) or an instance of ``Project``.

        Set the ``.enabled`` to ``False`` to exclude this project instead of deleting it."""
        if not isinstance(project, Project):
            try:
                project = Project.get(Project.name == project)
            except DoesNotExist:
                raise ValueError("{} is not a project".format(project))

        if project == self.current:
            self.deactivate()

        for backend in project.backends_resolved():
            backend.delete_project(project)

        project.delete_instance()
        shutil.rmtree(project.directory)

    def report(self):
        """Give a report on current projects, backend, and directory sizes.

        Returns tuples of ``(project name, backend name, and directory size (GB))``."""
        return sorted([(x.name, x.backends, get_dir_size(x.directory)) for x in self])
