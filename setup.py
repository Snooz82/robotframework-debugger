import re

from setuptools import setup
from setuptools import find_packages
from os.path import abspath, dirname, join

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
    long_description_content_type='text/markdown',
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
    install_requires=['robotframework >= 3.2.1'],
    python_requires='>=3.6',
)
