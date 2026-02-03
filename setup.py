# Hybrid versioning: single projection version as sum of all
# project components versions
import os
import subprocess

from setuptools import find_packages, setup


def read_version():
    """Read project version from VERSION file.

    Falls back to '0.0.0' if file missing (should not happen in release).
    """
    try:
        here = os.path.dirname(__file__)
        with open(os.path.join(here, "VERSION"), encoding="utf-8") as f:  # type: ignore
            return f.read().strip()
    except Exception:
        return "0.0.0"


__version__ = read_version()
__project__ = "penrose-lamarck"


def get_contributors() -> list[str]:
    """Extract unique contributors from git history."""
    try:
        result = subprocess.run(
            ["git", "shortlog", "-sne", "HEAD"], capture_output=True, text=True, check=True
        )
        contributors = []
        for line in result.stdout.splitlines():
            # Format: commits\tName <email>
            parts = line.strip().split("\t", 1)
            if len(parts) == 2:
                contributors.append(parts[1])
        return contributors
    except Exception:
        # Fall back to hardcoded list if git command fails
        return ["diogo <d.ogobaltazar+github@gmail.com>"]


__authors__ = get_contributors()
__author__ = ", ".join(__authors__)


def read(filename, parent=None):
    parent = parent or __file__
    try:
        with open(os.path.join(os.path.dirname(parent), filename)) as f:
            return f.read()
    except OSError:
        return ""


def parse_requirements(filename, parent=None):
    parent = parent or __file__
    filepath = os.path.join(os.path.dirname(parent), filename)
    content = read(filename, parent)

    for _line_number, line in enumerate(content.splitlines(), 1):
        candidate = line.strip()

        if candidate.startswith("-r"):
            for item in parse_requirements(candidate[2:].strip(), filepath):
                yield from item
        else:
            yield from candidate


# Use README.md as the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=__project__,
    version=__version__,
    author=", ".join(__author__),  # Use authors as a single string for the author field
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Project uses modern typing (PEP 585/604), requiring Python >= 3.10
    python_requires=">=3.10, <4",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=list(parse_requirements("src/penroselamarck/python-requirements.txt")),
    extras_require={
        # Developer utilities; keep minimal here since base image may include tools already
        "utils": [],
        # Testing dependencies pulled from tests/python-requirements.txt
        "test": list(parse_requirements("tests/python-requirements.txt")),
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
