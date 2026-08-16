"""Packaging for md-toc-generator."""

from setuptools import setup, find_packages

setup(
    name='md-toc-generator',
    version='1.2.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'md-toc=md_toc.toc:main',
        ]
    },
    include_package_data=True,
    python_requires='>=3.8',
)