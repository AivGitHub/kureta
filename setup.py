#!/usr/bin/env python3

import pathlib
from setuptools import find_packages, setup
import sys


class Main:

    def __init__(self, settings_name: str = 'settings.py', readme_name: str = 'README.md') -> None:
        # local variables
        _python_version: tuple = ()

        # self variables
        self._attributes_splitter: str = ' = '

        # Setter independent
        self.config_text = settings_name
        self.readme_text = readme_name

        # Setter from self.config_text
        self.attributes = self.config_text

        # Other
        _python_version = tuple(int(v) for v in self.attributes.get('PROJECT_PYTHON_REQUIRES').split('.'))

        if sys.version_info < _python_version:
            raise RuntimeError(f'This app works with Python {self.attributes.get("PROJECT_PYTHON_REQUIRES")}+')

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
        _attributes: dict = {}

        for _line in config_text.splitlines():
            _line = _line.strip()
            _parted = _line.split(self._attributes_splitter)

            try:
                __key = _parted[0]
                __value = _parted[1][1:-1]

                _attributes.update({__key: __value})
            except IndexError:
                continue

        self.__attributes = _attributes

    @staticmethod
    def get_text(file_name) -> str:
        return (pathlib.Path(__file__).parent / file_name).read_text('utf-8')


main = Main()


setup(
    name=main.attributes.get('PROJECT_NAME'),
    version=main.attributes.get('PROJECT_VERSION'),
    url=main.attributes.get('PROJECT_URL'),
    project_urls={
        'Source': main.attributes.get('PROJECT_SOURCE'),
        'Bug Tracker': main.attributes.get('PROJECT_BUG_TRACKER'),
    },
    license='MIT',
    author=main.attributes.get('PROJECT_AUTHOR'),
    author_email=main.attributes.get('PROJECT_AUTHOR_EMAIL'),
    description=main.attributes.get('PROJECT_DESCRIPTION'),
    long_description=main.readme_text,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'asgiref==3.5.0',
        'backports.zoneinfo==0.2.1',
        'Django==4.0.3',
        'psycopg2-binary==2.9.3',
        'python-magic==0.4.25',
        'sqlparse==0.4.2',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires=f'>={main.attributes.get("PROJECT_PYTHON_REQUIRES")}',
)
