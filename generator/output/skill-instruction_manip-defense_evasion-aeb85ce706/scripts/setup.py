# Build/install configuration for the package
from setuptools import setup, find_packages

setup(
    name="api-client-wrapper",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pytest>=6.0",
        "urllib3>=1.26.0"
    ],
    entry_points={
        "console_scripts": [
            "api-client-install=install:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
)