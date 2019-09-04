# -*- coding: utf-8 -*-
from . import BASE_DIR
from .filesystem import create_project_dir, get_dir_size
from .peewee import JSONField, SubstitutableDatabase
from peewee import Model, TextField, BlobField, BooleanField, DoesNotExist
import appdirs
import collections
import os
import shutil


class Project(Model):
    data = JSONField()
    backends = JSONField()
    directory = TextField()
    name = TextField(index=True, unique=True)
    default = BooleanField(default=False)
    active = BooleanField(default=True)

    def __str__(self):
        return "Project: {}".format(self.name)

    __repr__ = lambda x: str(x)

    def __lt__(self, other):
        # Allow ordering
        if not isinstance(other, ProjectDataset):
            raise TypeError
        else:
            return self.name.lower() < other.name.lower()


project_database = SubstitutableDatabase(BASE_DIR / "projects.db", [Project])


class ProjectManager(collections.abc.Iterable):
    def __init__(self):
        try:
            self.current = Project.get(Project.default == True)
        except DoesNotExist:
            self.current = None

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

    def select(self, name):
        if self.current:
            self.deactivate()
        self.activate(name)

    def create(self, name, backends=None, switch=True, default=False, **kwargs):
        if name in self:
            print("This project already exists; use "
                  "`projects.select({})` to switch.".format(name))

        if backend is None and 'default' not in backend_mapping:
            return MissingBackend("No `default` backend available; "
                                  "Must specify a project backend.")

        dirpath = create_project_dir(name)
        if default:
            Project.update(default=False).execute()
        Project.create(
            name=name,
            directory=dirpath,
            data=kwargs,
            backend=backend,
            default=default,
        )

        if switch:
            self.select(name)

    # def copy_project(self, new_name, switch=True, default=False):
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

    def use_temp_directory(self):
        """Point the ProjectManager towards a temporary directory instead of `user_data_dir`.

        Used exclusively for tests."""
        if not self._is_temp_dir:
            self._orig_base_data_dir = self._base_data_dir
            self._orig_base_logs_dir = self._base_logs_dir
        temp_dir = tempfile.mkdtemp()
        self._base_data_dir = os.path.join(temp_dir, "data")
        self._base_logs_dir = os.path.join(temp_dir, "logs")
        self.db.change_path(':memory:')
        self.select("tests-default")
        self._is_temp_dir = True
        return temp_dir
