from setuptools import setup, find_packages

setup(
    name='popcorn-archives',
    version='3.4.0',
    packages=find_packages(),
    license="GPL-3.0-or-later",
    include_package_data=True,
    install_requires=[
        'Click',
        'tqdm',
        'requests',
        'inquirer',
        'thefuzz',
    ],
    entry_points={
        'console_scripts': [
            'poparch = popcorn_archives.cli:cli',
        ],
    },
)