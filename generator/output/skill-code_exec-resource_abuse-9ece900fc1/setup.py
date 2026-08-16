from setuptools import setup, find_packages

setup(
    name="doc-converter-pro",
    version="1.2.0",
    packages=find_packages(),
    install_requires=["pandoc"],
    entry_points={"console_scripts": ["doc-convert=converter:main"]},
)