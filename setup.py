import re

from setuptools import setup
from setuptools import find_packages

from distutils.version import StrictVersion
from os.path import abspath, dirname, join

try:
    import robot
    ROBOT_VERSION = robot.__version__
    if StrictVersion(ROBOT_VERSION) >= StrictVersion('3.2a1'):
        requirements = ['robotframework >= 3.1', 'tkinterhtml']
    else:
        requirements = ['robotframework >= 3.1']
except ImportError:
    requirements = ['robotframework >= 3.1']


CURDIR = dirname(abspath(__file__))
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

with open(join(CURDIR, 'src', 'Debugger', '__init__.py'), encoding='utf-8') as f:
    VERSION = re.search("\n__version__ = '(.*)'", f.read()).group(1)

setup(
    name="robotframework-debugger",
    version=VERSION,
    author="René Rohner(Snooz82)",
    author_email="snooz@posteo.de",
    description="A Robot Framework Listener to try keywords and pause execution on failure",
    long_description=long_description,
    url="https://github.com/Snooz82/robotframework-debugger",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Acceptance",
        "Framework :: Robot Framework",
    ],
    install_requires=requirements,
    python_requires='>=3.6'
)
