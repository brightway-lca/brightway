from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

requirements = [
    'appdirs',
    'peewee',
]

test_requirements = ['pytest', 'bw-default-backend']

setup(
    name='brightway',
    version='3.0.dev',
    description='Python framework for Life Cycle Assessment',
    long_description=open(path.join(here, "README.md")).read(),
    url='https://github.com/pypa/sampleproject',
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
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
    tests_require=requirements + test_requirements,
)
