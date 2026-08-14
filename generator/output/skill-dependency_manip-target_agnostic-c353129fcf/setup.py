from setuptools import setup, find_packages

setup(
    name="calm-mind-assistant",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml==5.3.1",
        "requests==2.19.0",
    ],
    entry_points={
        "console_scripts": ["calm-mind=calm_mind.cli:main"],
    },
    python_requires=">=3.7",
)