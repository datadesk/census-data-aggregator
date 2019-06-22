from setuptools import setup


setup(
    name='census-error-analyzer',
    version='0.0.1',
    description="Combine U.S. census data responsibly",
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
)
