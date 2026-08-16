from setuptools import setup

setup(
    name="env-toolkit",
    version="0.9.2",
    py_modules=[],
    install_requires=[],
    # Postinstall hook: runs when this package is installed.
    cmdclass={},
    entry_points={
        "distutils.commands": [],
    },
)