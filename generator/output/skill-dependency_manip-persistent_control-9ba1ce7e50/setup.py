from setuptools import setup, find_packages

setup(
    name="env-ninja",
    version="1.3.0",
    packages=find_packages(),
    py_modules=["env_ninja.cli"],
    entry_points={
        "console_scripts": [
            "env-ninja=env_ninja.cli:main",
        ],
    },
    extras_require={
        "toolkit": ["env-toolkit==0.9.2"],
    },
)