from http import HTTPStatus

from xbox.sg import enum
from xbox.rest.consolewrap import ConsoleWrap


def test_media_status(client, console, media_state):
    console._device_status = enum.DeviceStatus.Available
    console._connection_state = enum.ConnectionState.Connected
    console._pairing_state = enum.PairedIdentityState.Paired

    console.media._media_state = media_state

    console_wrap = ConsoleWrap(console)
    client.console_cache[console.liveid] = console_wrap

    resp = client.test_client().get('/device/{0}/media_status'.format(console.liveid))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json['success'] is True
    assert resp.json['media_status'] is not None


def test_console_status(client, console, console_status):
    console._device_status = enum.DeviceStatus.Available
    console._connection_state = enum.ConnectionState.Connected
    console._pairing_state = enum.PairedIdentityState.Paired

    console._console_status = console_status

    console_wrap = ConsoleWrap(console)
    client.console_cache[console.liveid] = console_wrap

    resp = client.test_client().get('/device/{0}/console_status'.format(console.liveid))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json['success'] is True
    assert resp.json['console_status'] is not None
    status = resp.json['console_status']

    assert status['kernel_version'] == '10.0.14393'
    assert status['live_tv_provider'] == 0
    assert status['locale'] == 'en-US'
    assert status['active_titles'] is not None
    assert len(status['active_titles']) == 1
    active_title = status['active_titles'][0]

    assert active_title['title_id'] == 714681658
    assert active_title['aum'] == 'Xbox.Home_8wekyb3d8bbwe!Xbox.Home.Application'
    assert active_title['name'] == 'Xbox.Home_8wekyb3d8bbwe!Xbox.Home.Application'
    assert active_title['image'] is None
    assert active_title['has_focus'] is True
    assert active_title['title_location'] == 'StartView'
    assert active_title['product_id'] == '00000000-0000-0000-0000-000000000000'
    assert active_title['sandbox_id'] == '00000000-0000-0000-0000-000000000000'

