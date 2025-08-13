from setuptools import setup, find_packages

setup(
    name='popcorn-archives',
    version='1.0.0',
    packages=find_packages(),
    license="MIT",
    include_package_data=True,
    install_requires=[
        'Click',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'popcorn-archives = popcorn_archives.cli:cli',
        ],
    },
)