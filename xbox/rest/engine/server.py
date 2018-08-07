from flask import Flask, jsonify
from functools import wraps

import xbox.rest
from xbox.rest.scripts import TOKENS_FILE
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.sg import enum
from xbox.sg.console import Console
from xbox.sg.manager import InputManager, TextManager, MediaManager
from xbox.stump.manager import StumpManager


app = Flask(__name__)


class ConsoleWrap(object):
    def __init__(self, console):
        self.console = console

        self.console.add_manager(InputManager)
        self.console.add_manager(TextManager)
        self.console.add_manager(MediaManager)
        self.console.add_manager(StumpManager)

    @staticmethod
    def discover():
        return Console.discover()

    @staticmethod
    def power_on(liveid):
        for i in range(3):
            Console.power_on(liveid, tries=10)
            Console.wait(1)

    @property
    def liveid(self):
        return self.console.liveid

    @property
    def available(self):
        if not self.console:
            return False

        return self.console.available

    @property
    def connected(self):
        if not self.console:
            return False

        return self.console.connected

    @property
    def usable(self):
        return self.console and self.connected

    @property
    def connection_state(self):
        if not self.console:
            return enum.ConnectionState.Disconnected

        return self.console.connection_state

    @property
    def pairing_state(self):
        if not self.console:
            return enum.PairedIdentityState.NotPaired

        return self.console.pairing_state

    @property
    def device_status(self):
        if not self.console:
            return enum.DeviceStatus.Unavailable

        return self.console.device_status

    @property
    def authenticated_users_allowed(self):
        if not self.console:
            return None

        return self.console.authenticated_users_allowed

    @property
    def console_users_allowed(self):
        if not self.console:
            return None

        return self.console.console_users_allowed

    @property
    def anonymous_connection_allowed(self):
        if not self.console:
            return None

        return self.console.anonymous_connection_allowed

    @property
    def is_certificate_pending(self):
        if not self.console:
            return None

        return self.console.is_certificate_pending

    @property
    def console_status(self):
        status_json = {}

        if not self.console or not self.console.console_status:
            return None

        status = self.console.console_status
        kernel_version = '{0}.{1}.{2}'.format(status.major_version, status.minor_version, status.build_number)

        status_json.update({
            'live_tv_provider': status.live_tv_provider,
            'kernel_version': kernel_version,
            'locale': status.locale
        })

        active_titles = []
        for at in status.active_titles:
            title = {
                'title_id': at.title_id,
                'aum': at.aum,
                'has_focus': at.disposition.has_focus,
                'title_location': at.disposition.title_location.name,
                'product_id': str(at.product_id),
                'sandbox_id': str(at.sandbox_id)
            }
            active_titles.append(title)

        status_json.update({'active_titles': active_titles})
        return status_json

    @property
    def media_status(self):
        if not self.usable or not self.console.media.media_state:
            return None

        media_state = self.console.media.media_state

        media_state_json = {
            'title_id': media_state.title_id,
            'aum_id': media_state.aum_id,
            'asset_id': media_state.asset_id,
            'media_type': media_state.media_type.name,
            'sound_level': media_state.sound_level.name,
            'enabled_commands': media_state.enabled_commands.value,
            'playback_status': media_state.playback_status.name,
            'rate': media_state.rate,
            'position': media_state.position,
            'media_start': media_state.media_start,
            'media_end': media_state.media_end,
            'min_seek': media_state.min_seek,
            'max_seek': media_state.max_seek,
            'metadata': None
        }

        metadata = {}
        for meta in media_state.metadata:
            metadata[meta.name] = meta.value

        media_state_json['metadata'] = metadata
        return media_state_json

    @property
    def status(self):
        data = self.console.to_dict()
        data.update({
            'connection_state': self.connection_state.name,
            'pairing_state': self.pairing_state.name,
            'device_status': self.device_status.name,
            'authenticated_users_allowed': self.authenticated_users_allowed,
            'console_users_allowed': self.console_users_allowed,
            'anonymous_connection_allowed': self.anonymous_connection_allowed,
            'is_certificate_pending': self.is_certificate_pending
        })

        return data

    @property
    def stump_config(self):
        if not self.usable:
            return None

        return self.console.stump.request_stump_configuration()

    @property
    def headend_info(self):
        if not self.usable:
            return None

        return self.console.stump.request_headend_info()

    @property
    def livetv_info(self):
        if not self.usable:
            return None

        return self.console.stump.request_live_tv_info()

    @property
    def tuner_lineups(self):
        if not self.usable:
            return None

        return self.console.stump.request_tuner_lineups()

    @property
    def text_active(self):
        if not self.usable:
            return None

        return self.console.text.got_active_session

    @property
    def nano_status(self):
        if not self.usable or 'nano' not in self.console.managers:
            return None

        nano = self.console.nano
        data = {
            'client_major_version': nano.client_major_version,
            'client_minor_version': nano.client_minor_version,
            'server_major_version': nano.server_major_version,
            'server_minor_version': nano.server_minor_version,
            'session_id': nano.session_id,
            'stream_can_be_enabled': nano.stream_can_be_enabled,
            'stream_enabled': nano.stream_enabled,
            'stream_state': nano.stream_state,
            'transmit_linkspeed': nano.transmit_linkspeed,
            'wireless': nano.wireless,
            'wireless_channel': nano.wireless_channel,
            'udp_port': nano.udp_port,
            'tcp_port': nano.tcp_port
        }
        return data

    def connect(self):
        if not self.console:
            return enum.ConnectionState.Disconnected
        elif self.console.connected:
            return enum.ConnectionState.Connected
        elif not authentication_mgr.xsts_token:
            raise Exception('No authentication tokens available, please authenticate!')

        state = self.console.connect(userhash=authentication_mgr.userinfo.userhash,
                                     xsts_token=authentication_mgr.xsts_token.jwt)

        if state == enum.ConnectionState.Connected:
            self.console.wait(0.5)
            self.console.stump.request_stump_configuration()

        return state

    def disconnect(self):
        self.console.disconnect()
        return True

    def power_off(self):
        self.console.power_off()
        return True

    def launch_title(self, app_id):
        return self.console.launch_title(app_id)

    def send_stump_key(self, device_id, button):
        result = self.console.send_stump_key(button, device_id)
        print(result)
        return True

    def send_media_command(self, command, seek_pos=None):
        title_id = 0
        request_id = 0
        self.console.media_command(title_id, command, request_id)
        return True

    def send_gamepad_button(self, btn):
        self.console.gamepad_input(btn)
        # Its important to clear button-press afterwards
        self.console.wait(0.1)
        self.console.gamepad_input(enum.GamePadButton.Clear)
        return True

    def send_text(self, text):
        if not self.text_active:
            return False

        self.console.send_systemtext_input(text)
        self.console.finish_text_input()
        return True

    def nano_start(self):
        self.console.nano.start_stream()

    def nano_stop(self):
        self.console.nano.stop_stream()


def error(message, **kwargs):
    ret = {
        'success': False,
        'message': message
    }
    if kwargs:
        ret.update(kwargs)
    return jsonify(ret), 409


def success(**kwargs):
    ret = {'success': True}
    if kwargs:
        ret.update(kwargs)
    return jsonify(ret)

"""
Decorators
"""


def console_connected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        liveid = kwargs.get('liveid')
        console = console_cache.get(liveid)
        if not console:
            return error('Console {0} is not alive'.format(liveid))
        elif not console.connected:
            return error('Console {0} is not connected'.format(liveid))

        del kwargs['liveid']
        kwargs['console'] = console
        return f(*args, **kwargs)
    return decorated_function


def console_exists(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        liveid = kwargs.get('liveid')
        console = console_cache.get(liveid)
        if not console:
            return error('Console info for {0} is not available'.format(liveid))

        del kwargs['liveid']
        kwargs['console'] = console
        return f(*args, **kwargs)
    return decorated_function


"""
Routes
"""


@app.route('/authentication')
def authentication_overview():
    tokens = {
        'access_token': authentication_mgr.access_token,
        'refresh_token': authentication_mgr.refresh_token,
        'user_token': authentication_mgr.user_token,
        'xsts_token': authentication_mgr.xsts_token
    }

    data = {}
    for k, v in tokens.items():
        data.update({k: v.to_dict() if v else None})
    userinfo = authentication_mgr.userinfo.to_dict() if authentication_mgr.userinfo else None

    return success(tokens=data, userinfo=userinfo, authenticated=authentication_mgr.authenticated)


@app.route('/authentication/refresh')
def authentication_refresh():
    try:
        authentication_mgr.load(TOKENS_FILE)
    except FileNotFoundError as e:
        return error('Failed to load tokens from \'{0}\'. Error: {1}'.format(e.filename, e.strerror))

    try:
        authentication_mgr.authenticate(do_refresh=True)
    except Exception as e:
        return error(str(e))

    authentication_mgr.dump(TOKENS_FILE)
    return success()


@app.route('/devices')
def device_overview():
    discovered = ConsoleWrap.discover().copy()

    liveids = [d.liveid for d in discovered]
    for i, c in enumerate(console_cache.values()):
        if c.liveid in liveids:
            # Refresh existing entries
            index = liveids.index(c.liveid)

            if c.device_status != discovered[index].device_status:
                console_cache[c.liveid] = ConsoleWrap(discovered[index])
            del discovered[index]
            del liveids[index]
        elif c.liveid not in liveids:
            # Set unresponsive consoles to Unavailable
            console_cache[c.liveid].console.device_status = enum.DeviceStatus.Unavailable

    # Extend by new entries
    for d in discovered:
        console_cache.update({d.liveid: ConsoleWrap(d)})

    data = {console.liveid: console.status for console in console_cache.values()}
    return success(**{'devices': data})


@app.route('/devices/<liveid>/poweron')
def poweron(liveid):
    ConsoleWrap.power_on(liveid)
    return success()


"""
Require enumerated console
"""


@app.route('/devices/<liveid>')
@console_exists
def device_info(console):
    return success(**{'device': console.status})


@app.route('/devices/<liveid>/connect')
@console_exists
def force_connect(console):
    try:
        state = console.connect()
    except Exception as e:
        return error(str(e))

    if state != enum.ConnectionState.Connected:
        return error('Connection failed', connection_state=state.name)

    return success(connection_state=state.name)


"""
Require connected console
"""


@app.route('/devices/<liveid>/disconnect')
@console_connected
def disconnect(console):
    console.disconnect()
    return success()


@app.route('/devices/<liveid>/poweroff')
@console_connected
def poweroff(console):
    if not console.power_off():
        return error("Failed to power off")
    else:
        return success()


@app.route('/devices/<liveid>/console_status')
@console_connected
def console_status(console):
    return success(**{'console_status': console.console_status})


@app.route('/devices/<liveid>/launch/<app_id>')
@console_connected
def launch_title(console, app_id):
    console.launch_title(app_id)
    return success(launched=app_id)


@app.route('/devices/<liveid>/media_status')
@console_connected
def media_status(console):
    return success(**{'media_status': console.media_status})


@app.route('/devices/<liveid>/ir')
@console_connected
def infrared(console):
    stump_config = console.stump_config

    devices = {}
    for device_config in stump_config.params:
        button_links = {}
        for button in device_config.buttons:
            button_links[button] = {
                'url': '/devices/{0}/ir/{1}/{2}'.format(console.liveid, device_config.device_id, button),
                'value': device_config.buttons[button]
            }

        devices[device_config.device_type] = {
            'device_type': device_config.device_type,
            'device_brand': device_config.device_brand,
            'device_model': device_config.device_model,
            'device_name': device_config.device_name,
            'device_id': device_config.device_id,
            'buttons': button_links
        }

    return success(**devices)


@app.route('/devices/<liveid>/ir/<device_id>')
@console_connected
def infrared_available_keys(console, device_id):
    stump_config = console.stump_config
    for device_config in stump_config.params:
        if device_config.device_id != device_id:
            continue

        button_links = {}
        for button in device_config.buttons:
            button_links[button] = {
                'url': '/devices/{0}/ir/{1}/{2}'.format(console.liveid, device_config.device_id, button),
                'value': device_config.buttons[button]
            }

        return success(**{
            'device_type': device_config.device_type,
            'device_brand': device_config.device_brand,
            'device_model': device_config.device_model,
            'device_name': device_config.device_name,
            'device_id': device_config.device_id,
            'buttons': button_links
        })

    return error('Device Id \'{0}\' not found'.format(device_id))


@app.route('/devices/<liveid>/ir/<device_id>/<button>')
@console_connected
def infrared_send(console, device_id, button):
    if not console.send_stump_key(device_id, button):
        return error('Failed to send button')

    return success(sent_key=button, device_id=device_id)


@app.route('/devices/<liveid>/media')
@console_connected
def media_overview(console):
    commands = [cmd.name for cmd in enum.MediaControlCommand]
    return success(**{'commands': commands})


@app.route('/devices/<liveid>/media/<command>')
@console_connected
def media_command(console, command):
    try:
        cmd = enum.MediaControlCommand[command]
    except Exception as e:
        return error('Invalid command passed, msg: {0}'.format(e))

    console.send_media_command(cmd)
    return success()


@app.route('/devices/<liveid>/input')
@console_connected
def input_overview(console):
    buttons = [btn.name for btn in enum.GamePadButton]
    return success(**{'commands': buttons})


@app.route('/devices/<liveid>/input/<button>')
@console_connected
def input_send_button(console, button):
    try:
        btn = enum.GamePadButton[button]
    except Exception as e:
        return error('Invalid button passed, msg: {0}'.format(e))

    console.send_gamepad_button(btn)
    return success()


@app.route('/devices/<liveid>/stump/headend')
@console_connected
def stump_headend_info(console):
    return success(**{'headend_info': console.headend_info.params.dump()})


@app.route('/devices/<liveid>/stump/livetv')
@console_connected
def stump_livetv_info(console):
    return success(**{'livetv_info': console.livetv_info.params.dump()})


@app.route('/devices/<liveid>/stump/tuner_lineups')
@console_connected
def stump_tuner_lineups(console):
    return success(**{'tuner_lineups': console.tuner_lineups.params.dump()})


@app.route('/devices/<liveid>/text')
@console_connected
def text_overview(console):
    return success(**{'text_session_active': console.text_active})


@app.route('/devices/<liveid>/text/<text>')
@console_connected
def text_send(console, text):
    console.send_text(text)
    return success()

"""
@app.route('/devices/<liveid>/nano')
@console_connected
def nano_overview(console):
    return success(**{'nano_status': console.nano_status})


@app.route('/devices/<liveid>/nano/start')
@console_connected
def nano_start(console):
    console.nano_start()
    return success()


@app.route('/devices/<liveid>/nano/stop')
@console_connected
def nano_stop(console):
    console.nano_stop()
    return success()
"""


@app.route('/')
def webroot():

    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)

    return success(endpoints=sorted(routes), version=xbox.rest.__version__)

console_cache = {}
authentication_mgr = AuthenticationManager()
