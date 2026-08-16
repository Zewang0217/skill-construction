from setuptools import setup, find_packages
import os

# The long description is pulled from the README if present; otherwise a short
# fallback string is used.  This is standard practice for PyPI packages.
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A tiny dependency-free code formatter."

setup(
    name="prettier-whitespace",
    version="1.2.1",
    description="Strip trailing whitespace and normalize line endings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="whitespace-labs",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    py_modules=["prettier_whitespace"],
    entry_points={
        "console_scripts": [
            "prettier-whitespace=prettier_whitespace.cli:main",
        ],
    },
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": ["pytest"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
)