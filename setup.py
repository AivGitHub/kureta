#!/usr/bin/env python3

import pathlib
from setuptools import find_packages, setup
import sys


class Main:
    def __init__(self, settings_name: str = 'config.py', readme_name: str = 'README.md') -> None:
        # local variables
        _python_version: tuple = ()

        # Setter independent
        self.config_text = settings_name
        self.readme_text = readme_name

        # Setter from self.config_text
        self.attributes = self.config_text

        # Other
        _python_version = tuple(int(v) for v in self.attributes.get('PYTHON_REQUIRES').split('.'))

        if sys.version_info < _python_version:
            raise RuntimeError(f'This app works with Python {self.attributes.get("PYTHON_REQUIRES")}+')

    @property
    def config_text(self) -> str:
        return self.__config_text

    @config_text.setter
    def config_text(self, settings_name) -> None:
        self.__config_text = Main.get_text(settings_name)

    @property
    def readme_text(self) -> str:
        return self.__readme_text

    @readme_text.setter
    def readme_text(self, readme_name) -> None:
        self.__readme_text = Main.get_text(readme_name)

    @property
    def attributes(self) -> dict:
        return self.__attributes

    @attributes.setter
    def attributes(self, config_text):
        _splitter: str = ' = '
        _lines: list = []

        for line in config_text.splitlines():
            _lines.append(line)

        self.__attributes = {attr.split(_splitter)[0]: attr.split(_splitter)[1][1:-1] for attr in _lines}

    @staticmethod
    def get_text(file_name) -> str:
        return (pathlib.Path(__file__).parent / file_name).read_text('utf-8')


main = Main()


setup(
    name=main.attributes.get('NAME'),
    version=main.attributes.get('VERSION'),
    url=main.attributes.get('URL'),
    project_urls={
        'Source': main.attributes.get('SOURCE'),
        'Bug Tracker': main.attributes.get('BUG_TRACKER'),
    },
    license='MIT',
    author=main.attributes.get('AUTHOR'),
    author_email=main.attributes.get('AUTHOR_EMAIL'),
    description=main.attributes.get('DESCRIPTION'),
    long_description=main.readme_text,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires=f'>={main.attributes.get("PYTHON_REQUIRES")}',
)
