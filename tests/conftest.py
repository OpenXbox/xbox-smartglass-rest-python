import pytest
import uuid
from binascii import unhexlify

from xbox.sg import enum
from xbox.sg.console import Console

from xbox.rest.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    yield app.test_client()


@pytest.fixture(scope='session')
def console_address():
    return '10.11.12.12'


@pytest.fixture(scope='session')
def console_name():
    return 'TestConsole'


@pytest.fixture(scope='session')
def console_uuid():
    return uuid.UUID('de305d54-75b4-431b-adb2-eb6b9e546014')


@pytest.fixture(scope='session')
def console_liveid():
    return 'FD0000123456789'


@pytest.fixture(scope='session')
def console_flags():
    return enum.PrimaryDeviceFlag.AllowAnonymousUsers | enum.PrimaryDeviceFlag.AllowAuthenticatedUsers


@pytest.fixture(scope='session')
def console_public_key():
    return unhexlify(
        b'041815d5382df79bd792a8d8342fbc717eacef6a258f779279e5463573e06b'
        b'f84c6a88fac904870bf3a26f856e65f483195c4323eef47a048f23a031da6bd0929d'
    )


@pytest.fixture
def console(console_address, console_name, console_uuid,
            console_liveid, console_flags, console_public_key):
    return Console(
        address=console_address,
        name=console_name,
        uuid=console_uuid,
        liveid=console_liveid,
        flags=console_flags,
        public_key=console_public_key
    )
