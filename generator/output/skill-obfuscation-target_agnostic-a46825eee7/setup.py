"""Packaging for env-doctor."""

from setuptools import setup, find_packages

setup(
    name="env-doctor",
    version="1.2.0",
    description="Environment variable management tool",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
    ],
    entry_points={
        "console_scripts": [
            "env-doctor=env_doctor.core:main",
        ],
    },
    python_requires=">=3.7",
)