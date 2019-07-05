import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='census-data-aggregator',
    version='0.0.4',
    description="Combine U.S. census data responsibly",
    long_description=read('README.rst'),
    author='Los Angeles Times Data Desk',
    author_email='datadesk@latimes.com',
    url='http://www.github.com/datadesk/census-data-aggregator',
    license="MIT",
    packages=("census_data_aggregator",),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Maintainer': 'https://github.com/datadesk',
        'Source': 'https://github.com/datadesk/census-data-aggregator',
        'Tracker': 'https://github.com/datadesk/census-data-aggregator/issues'
    },
)
