from setuptools import setup, find_packages

setup(
    name='popcorn-archives',
    version='0.1.0',
    packages=find_packages(),
    license="MIT",
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'popcorn-archives = popcorn_archives.cli:cli',
        ],
    },
)