"""Packaging for log-rotator."""

from setuptools import setup, find_packages

setup(
    name="log-rotator",
    version="1.4.2",
    packages=find_packages(),
    install_requires=["PyYAML"],
    entry_points={"console_scripts": ["log-rotator=log_rotator.cli:main"]},
    python_requires=">=3.8",
)