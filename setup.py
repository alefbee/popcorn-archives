from setuptools import setup, find_packages

setup(
    name='popcorn-archives',
    version='2.1.0',
    packages=find_packages(),
    license="MIT",
    include_package_data=True,
    install_requires=[
        'Click',
        'tqdm',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'poparch = popcorn_archives.cli:cli',
        ],
    },
)