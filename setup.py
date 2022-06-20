import os

from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="census-data-aggregator",
    version="0.0.6",
    description="Combine U.S. census data responsibly",
    long_description=read("README.rst"),
    author="Ben Welsh",
    author_email="b@palewi.re",
    url="http://www.github.com/datadesk/census-data-aggregator",
    license="MIT",
    packages=("census_data_aggregator",),
    install_requires=[
        "numpy",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Maintainer": "https://github.com/datadesk",
        "Source": "https://github.com/datadesk/census-data-aggregator",
        "Tracker": "https://github.com/datadesk/census-data-aggregator/issues",
    },
)
