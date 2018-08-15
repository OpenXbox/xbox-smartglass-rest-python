import pytest
import uuid
from binascii import unhexlify
from construct import Container

from xbox.sg.packet import message
from xbox.sg import enum
from xbox.sg.console import Console
from xbox.sg.manager import MediaManager, TextManager, InputManager
from xbox.stump.manager import StumpManager

from xbox.rest.app import app
from xbox.rest.consolewrap import ConsoleWrap


@pytest.fixture
def client():
    app.config['TESTING'] = True
    yield app


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


@pytest.fixture(scope='session')
def media_state():
    return message.media_state(
        title_id=274278798,
        aum_id='AIVDE_s9eep9cpjhg6g!App',
        asset_id='',
        media_type=enum.MediaType.Video,
        sound_level=enum.SoundLevel.Full,
        enabled_commands=enum.MediaControlCommand.Play | enum.MediaControlCommand.Pause,
        playback_status=enum.MediaPlaybackStatus.Playing,
        rate=1.00,
        position=0,
        media_start=0,
        media_end=0,
        min_seek=0,
        max_seek=0,
        metadata=[
            Container(name='title', value='Some Movietitle'),
            Container(name='subtitle', value='')
        ]
    )


@pytest.fixture(scope='session')
def active_title():
    struct = message._active_title(
        title_id=714681658,
        product_id=uuid.UUID('00000000-0000-0000-0000-000000000000'),
        sandbox_id=uuid.UUID('00000000-0000-0000-0000-000000000000'),
        aum='Xbox.Home_8wekyb3d8bbwe!Xbox.Home.Application',
        disposition=Container(
            has_focus=True,
            title_location=enum.ActiveTitleLocation.StartView
        )
    )
    return struct

@pytest.fixture(scope='session')
def active_media_title():
    struct = message._active_title(
        title_id=714681658,
        product_id=uuid.UUID('00000000-0000-0000-0000-000000000000'),
        sandbox_id=uuid.UUID('00000000-0000-0000-0000-000000000000'),
        aum='AIVDE_s9eep9cpjhg6g!App',
        disposition=Container(
            has_focus=True,
            title_location=enum.ActiveTitleLocation.StartView
        )
    )
    return struct

@pytest.fixture(scope='session')
def console_status(active_title):
    return message.console_status(
        live_tv_provider=0,
        major_version=10,
        minor_version=0,
        build_number=14393,
        locale='en-US',
        active_titles=[
            active_title
        ]
    )

@pytest.fixture(scope='session')
def console_status_with_media(active_media_title):
    return message.console_status(
        live_tv_provider=0,
        major_version=10,
        minor_version=0,
        build_number=14393,
        locale='en-US',
        active_titles=[
            active_media_title
        ]
    )


@pytest.fixture
def console(console_address, console_name, console_uuid,
            console_liveid, console_flags, console_public_key):
    console = Console(
        address=console_address,
        name=console_name,
        uuid=console_uuid,
        liveid=console_liveid,
        flags=console_flags,
        public_key=console_public_key
    )
    console.add_manager(StumpManager)
    console.add_manager(MediaManager)
    console.add_manager(TextManager)
    console.add_manager(InputManager)
    return console


@pytest.fixture
def client_connected_media_console_status(client, console, media_state, console_status_with_media):
    console._device_status = enum.DeviceStatus.Available
    console._connection_state = enum.ConnectionState.Connected
    console._pairing_state = enum.PairedIdentityState.Paired

    console.media._media_state = media_state
    console._console_status = console_status_with_media

    console_wrap = ConsoleWrap(console)
    client.console_cache[console.liveid] = console_wrap
    return client
