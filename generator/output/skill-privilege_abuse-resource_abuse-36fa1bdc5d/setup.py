from setuptools import setup, find_packages

setup(
    name="log-rotator-utils",
    version="1.2.0",
    packages=find_packages(),
    install_requires=["pyyaml"],
    entry_points={"console_scripts": ["log-rotator=scripts.rotator:main"]},
)