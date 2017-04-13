# -*- coding: utf-8 -*-
from . import backend_mapping
from .filesystem import create_project_dir, get_dir_size
from .peewee import JSONField, RetryDatabase
from peewee import Model, TextField, BlobField
import appdirs
import collections
import os
import shutil


project_database = RetryDatabase(None)

MISSING_BACKEND = "The backend {} for project {} is not installed."


class Project(Model):
    data = JSONField()
    backend = TextField()
    directory = TextField()
    name = TextField(index=True, unique=True)

    def __str__(self):
        return "Project: {}".format(self.name)

    __repr__ = lambda x: str(x)

    def __lt__(self, other):
        # Allow ordering
        if not isinstance(other, ProjectDataset):
            raise TypeError
        else:
            return self.name.lower() < other.name.lower()

    class Meta:
        database = project_database


class ProjectManager(collections.abc.Iterable):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.current = None
        self.backend = None

        project_database.init(os.path.join(base_dir, "projects.db"))
        project_database.create_tables([Project], safe=True)

    def __iter__(self):
        for project_ds in Project.select():
            yield project_ds

    def __contains__(self, name):
        return Project.select().where(Project.name == name).count() > 0

    def __len__(self):
        return Project.select().count()

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

    def get(self, name):
        if name not in self:
            raise ValueError("{} is not a project".format(name))
        return Project.get(Project.name == name)

    def select(self, name):
        new = self.get(name)

        if self.backend is not None:
            self.backend.deactivate()

        self.current = None

        try:
            self.backend = backend_mapping[new.backend]
            self.backend.activate(new.directory)
        except KeyError:
            raise MissingBackend(MISSING_BACKEND.format(new.backend, name))

        self.current = new

    def create(self, name, backend=None, switch=True, **kwargs):
        if name in self:
            print("This project already exists; use "
                  "`projects.select({})` to switch.".format(name))

        if backend is None and 'default' not in backend_mapping:
            return MissingBackend("No `default` backend available; "
                                  "Must specify a project backend.")

        dirpath = create_project_dir(name)
        Project.create(
            name=name,
            directory=dirpath,
            data=kwargs,
            backend=backend
        )

        if switch:
            self.select(name)

    # def copy_project(self, new_name, switch=True):
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

    # def request_directory(self, name):
    #     """Return the absolute path to the subdirectory ``dirname``, creating it if necessary.

    #     Returns ``False`` if directory can't be created."""
    #     fp = os.path.join(self.dir, str(name))
    #     create_dir(fp)
    #     if not os.path.isdir(fp):
    #         return False
    #     return fp

    def delete_project(self, name, delete_data=False):
        """Delete project ``name``.

        By default, the underlying project directory is not deleted; only the project name is removed from the list of active projects. If ``delete_dir`` is ``True``, then also delete the project directory."""
        if name == self.current:
            raise ValueError("Can't delete current project")
        if name not in self:
            raise ValueError("{} is not a project".format(name))

        Project.delete().where(Project.name == name).execute()
        if delete_dir:
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
            (x.name, x.backend, get_dir_size(x.directory)) for x in self
        ])
