import importlib
import pathlib
import subprocess

from django.core.checks.security.base import SECRET_KEY_INSECURE_PREFIX
from django.core.management.utils import get_random_secret_key

from kureta.exceptions import (
    InitializeBoostrapException,
    InitializeDatabaseException,
    InitializeFixturesException,
    InitializeMigrationException,
    WrongSettingsFileContentException
)
import settings


class Static:

    FILES = (
        {
            'target_name': 'bootstrap',
            'link': 'https://github.com/twbs/bootstrap/releases/download/v5.1.3/bootstrap-5.1.3-dist.zip'
        },
        {
            'target_name': 'fontawesome',
            'link': 'https://use.fontawesome.com/releases/v6.0.0/fontawesome-free-6.0.0-web.zip'
        }
    )

    def __init__(self):
        pass

    @staticmethod
    def download_file(file_name, path):
        _cmd = f'wget {file_name} -P {path}'
        _process = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _out, _err = _process.communicate()

        if _process.returncode != 0:
            raise InitializeBoostrapException(_err.decode('utf-8'))

    @staticmethod
    def extract_file(zip_path, path):
        _cmd = f'7z x {zip_path} -O./{path}'
        _process = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _out, _err = _process.communicate()

        if _process.returncode != 0:
            raise InitializeBoostrapException(_err.decode('utf-8'))

    def initialize(self, files=None, override=True):
        if not files:
            files = self.FILES

        if settings.DEBUG:
            _lib_path = pathlib.Path(settings.STATIC_URL)
        else:
            _lib_path = pathlib.Path(settings.STATIC_ROOT)

        _lib_path = _lib_path / 'external_lib'
        _lib_path.mkdir(parents=True, exist_ok=True)

        for _file in files:
            __target_name = _file.get('target_name')

            if not override and (_lib_path / __target_name).exists():
                return None

            __link = _file.get('link')
            __zip_name = __link.split('/')[-1]
            __original_name = __zip_name.split('.zip')[0]

            __zip_path = _lib_path / __zip_name

            Static.download_file(__link, _lib_path)
            Static.extract_file(__zip_path, _lib_path)

            __zip_path.unlink()

            (_lib_path / __original_name).rename(_lib_path / __target_name)

    def initialize_bootstrap(self, override=True):
        _file = tuple(f for f in self.FILES if f.get('target_name') == 'bootstrap')

        self.initialize(files=_file, override=override)

    def initialize_fontawesome(self, override=True):
        _file = tuple(f for f in self.FILES if f.get('target_name') == 'fontawesome')

        self.initialize(files=_file, override=override)


class Database:

    __REQUIRED_FIELDS = ('DEFAULT_DATABASE_PASSWORD', 'SECRET_KEY')

    PSQL_CONSOLE_COMMAND = 'sudo -u postgres psql -t'
    FIXTURES_CONSOLE_COMMAND = 'python manage.py loaddata'
    MIGRATION_COMMANDS = ('python manage.py makemigrations', 'python manage.py migrate')
    FIXTURES = ('mail/fixtures/mail_servers.json',)

    def __init__(self, settings_file: str = 'secure.py', secure: bool = False, ignore=True) -> None:
        """
        TODO: Add support for multiple database initialization
        """
        self.databases = settings.DATABASES.keys()

        self.database_name: str = settings.PROJECT_NAME
        self.settings_file: pathlib.Path = pathlib.Path(settings_file)
        self.secure: bool = secure
        self.ignore: bool = ignore

        _secret_parameters: dict = self.__get_secret_parameters()

        self.__database_password: str = _secret_parameters.get('DEFAULT_DATABASE_PASSWORD')
        self.__secret_key: str = _secret_parameters.get('SECRET_KEY')

    def __str__(self) -> str:
        return self.database_name

    def initialize_settings_file(self) -> None:
        _data: str = ''
        _lines: list = []
        _secret_key: str = get_random_secret_key()

        if self.settings_file.exists():
            if self.ignore:
                return None
            else:
                raise FileExistsError(f'File {self.settings_file} exists!')

        if not self.secure:
            _secret_key = f'{SECRET_KEY_INSECURE_PREFIX}{_secret_key}'

        _lines.append(f'SECRET_KEY = \'{_secret_key}\'')
        _lines.append(f'DEFAULT_DATABASE_PASSWORD = \'{get_random_secret_key()}\'')

        _data = '\n'.join(_lines)

        self.settings_file.touch()
        self.settings_file.write_text(f'{_data}\n')

    def initialize_database(self) -> None:
        _create_database_file: pathlib.Path = pathlib.Path('create_database.tmp.sql')
        _commands: tuple = (
            f'CREATE DATABASE {settings.PROJECT_NAME};',
            f'CREATE USER {settings.PROJECT_NAME} WITH ENCRYPTED PASSWORD \'{self.__database_password}\';',
            f'GRANT ALL PRIVILEGES ON DATABASE {settings.PROJECT_NAME} TO {settings.PROJECT_NAME};'
        )

        if _create_database_file.exists():
            _create_database_file.unlink()

        _create_database_file.write_text('\n'.join(_commands))

        _cmd = f'cat {_create_database_file} | {self.PSQL_CONSOLE_COMMAND}'
        _process = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _out, _err = _process.communicate()

        _create_database_file.unlink()

        if _process.returncode != 0:
            raise InitializeDatabaseException(_err.decode('utf-8'))

    def initialize_migrations(self) -> None:
        for _cmd in self.MIGRATION_COMMANDS:
            _process = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _out, _err = _process.communicate()

            if _process.returncode != 0:
                raise InitializeMigrationException(_err.decode('utf-8'))

    def initialize_fixtures(self) -> None:
        # Initialize fixture by fixture.
        for _fixture in self.FIXTURES:
            _cmd = f'{self.FIXTURES_CONSOLE_COMMAND} {_fixture}'
            _process = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _out, _err = _process.communicate()

            if _process.returncode != 0:
                raise InitializeFixturesException(_err.decode('utf-8'))

    def initialize(self) -> None:
        self.initialize_settings_file()
        self.initialize_database()
        self.initialize_migrations()
        self.initialize_fixtures()

    def __get_secret_parameters(self) -> dict:
        try:
            __file_name, __extension = self.settings_file.name.split('.')
        except IndexError:
            __file_name, __extension = self.settings_file.name, ''

        if self.settings_file.exists():
            _secure = importlib.import_module(__file_name)

            try:
                return {
                    'DEFAULT_DATABASE_PASSWORD': _secure.DEFAULT_DATABASE_PASSWORD,
                    'SECRET_KEY': _secure.SECRET_KEY
                }
            except AttributeError:
                raise WrongSettingsFileContentException(
                    f'{", ".join(self.__REQUIRED_FIELDS)} are required in {self.settings_file}')

        __secret_key = get_random_secret_key()
        __database_password = get_random_secret_key()

        if not self.secure:
            _secret_key = f'{SECRET_KEY_INSECURE_PREFIX}{__secret_key}'
            __database_password = f'{SECRET_KEY_INSECURE_PREFIX}{__database_password}'

        return {'DEFAULT_DATABASE_PASSWORD': __database_password, 'SECRET_KEY': __secret_key}
