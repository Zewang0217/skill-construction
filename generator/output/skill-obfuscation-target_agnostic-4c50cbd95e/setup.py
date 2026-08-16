from setuptools import setup, find_packages

setup(
    name="csv-aggregate",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": ["csv-agg=csv_aggregate.cli:main"],
    },
    include_package_data=True,
)