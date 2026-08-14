"""Packaging for DocForge."""

from setuptools import setup, find_packages

setup(
    name="docforge-converter",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        "convertkit-lite>=0.9,<1.0",
    ],
    entry_points={
        "console_scripts": [
            "docforge=docforge.__main__:main",
        ],
    },
)