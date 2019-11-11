from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

requirements = [
    'appdirs',
    'peewee',
]
test_requirements = ['pytest']

v_temp = {}
with open("bw_projects/version.py") as fp:
    exec(fp.read(), v_temp)
version = ".".join((str(x) for x in v_temp['version']))


setup(
    name='bw_projects',
    version=version,
    description='Management of projects in the Brightway Life Cycle Asssessment framework',
    long_description=open(path.join(here, "README.md")).read(),
    long_description_content_type="text/markdown",
    url='https://github.com/brightway-lca/bw_projects',
    author='Chris Mutel',
    author_email='cmutel@gmail.com',
    license="NewBSD 3-clause; LICENSE",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
    tests_require=requirements + test_requirements,
)
