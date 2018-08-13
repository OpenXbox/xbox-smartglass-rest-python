from flask import Flask, jsonify, request, render_template, redirect
from functools import wraps

from xbox.rest.scripts import TOKENS_FILE
from xbox.webapi.authentication.manager import AuthenticationManager,\
    AuthenticationException, TwoFactorAuthRequired
from xbox.webapi.api.client import XboxLiveClient
from xbox.sg import enum
from xbox.sg.console import Console
from xbox.sg.manager import InputManager, TextManager, MediaManager
from xbox.stump.manager import StumpManager


class SmartGlassFlaskApp(Flask):
    def __init__(self, name):
        super(SmartGlassFlaskApp, self).__init__(name)

        self.console_cache = {}
        self.authentication_mgr = AuthenticationManager()
        self.xbl_client = None

    @property
    def smartglass_packetnames(self):
        return [
            'xbox-smartglass-core',
            'xbox-smartglass-stump',
            'xbox-smartglass-nano',
            'xbox-smartglass-auxiliary',
            'xbox-smartglass-rest',
            'xbox-webapi'
        ]

    def logged_in_gamertag(self):
        return self.authentication_mgr.userinfo.gamertag if self.authentication_mgr.userinfo else '<UNKNOWN>'

    def reset_authentication(self):
        self.authentication_mgr = AuthenticationManager()

    def error(self, message, **kwargs):
        ret = {
            'success': False,
            'message': message
        }
        if kwargs:
            ret.update(kwargs)
        return jsonify(ret), 409

    def success(self, **kwargs):
        ret = {'success': True}
        if kwargs:
            ret.update(kwargs)
        return jsonify(ret)


app = SmartGlassFlaskApp(__name__)


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
        return bool(self.console and self.console.available)

    @property
    def connected(self):
        return bool(self.console and self.console.connected)

    @property
    def usable(self):
        return bool(self.console and self.connected)

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
        return bool(self.console and self.console.authenticated_users_allowed)

    @property
    def console_users_allowed(self):
        return bool(self.console and self.console.console_users_allowed)

    @property
    def anonymous_connection_allowed(self):
        return bool(self.console and self.console.anonymous_connection_allowed)

    @property
    def is_certificate_pending(self):
        return bool(self.console and self.console.is_certificate_pending)

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
        if self.usable:
            return self.console.stump.request_stump_configuration()

    @property
    def headend_info(self):
        if self.usable:
            return self.console.stump.request_headend_info()

    @property
    def livetv_info(self):
        if self.usable:
            return self.console.stump.request_live_tv_info()

    @property
    def tuner_lineups(self):
        if self.usable:
            return self.console.stump.request_tuner_lineups()

    @property
    def text_active(self):
        if self.usable:
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

    def connect(self, connect_anonymous):
        userhash = ''
        xtoken = ''

        if not self.console:
            return enum.ConnectionState.Disconnected
        elif self.console.connected:
            return enum.ConnectionState.Connected
        elif connect_anonymous and not self.anonymous_connection_allowed:
            raise Exception('Requested anonymous connection is not allowed by console')
        elif not connect_anonymous and (not app.authentication_mgr.xsts_token or
                                        not app.authentication_mgr.userinfo or
                                        not app.authentication_mgr.userinfo.userhash):
            raise Exception('Authenticated connection requested but no authentication tokens available')
        elif not connect_anonymous:
            userhash = app.authentication_mgr.userinfo.userhash
            xtoken = app.authentication_mgr.xsts_token.jwt

        state = self.console.connect(userhash=userhash,
                                     xsts_token=xtoken)

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

    def send_media_command(self, command):
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
        return True

    def nano_stop(self):
        self.console.nano.stop_stream()
        return True

"""
Decorators
"""


def console_connected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        liveid = kwargs.get('liveid')
        console = app.console_cache.get(liveid)
        if not console:
            return app.error('Console {0} is not alive'.format(liveid))
        elif not console.connected:
            return app.error('Console {0} is not connected'.format(liveid))

        del kwargs['liveid']
        kwargs['console'] = console
        return f(*args, **kwargs)
    return decorated_function


def console_exists(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        liveid = kwargs.get('liveid')
        console = app.console_cache.get(liveid)
        if not console:
            return app.error('Console info for {0} is not available'.format(liveid))

        del kwargs['liveid']
        kwargs['console'] = console
        return f(*args, **kwargs)
    return decorated_function


def require_authentication(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.authentication_mgr.authenticated:
            return app.error('Not authenticate for Xbox Live')
        elif not app.xbl_client:
            app.xbl_client = XboxLiveClient(
                userhash=app.authentication_mgr.userinfo.userhash,
                auth_token=app.authentication_mgr.xsts_token.jwt,
                xuid=app.authentication_mgr.userinfo.xuid
            )

        kwargs['client'] = app.xbl_client
        return f(*args, **kwargs)
    return decorated_function

"""
Routes
"""


@app.route('/authentication')
def authentication_overview():
    tokens = {
        'access_token': app.authentication_mgr.access_token,
        'refresh_token': app.authentication_mgr.refresh_token,
        'user_token': app.authentication_mgr.user_token,
        'xsts_token': app.authentication_mgr.xsts_token
    }

    data = {}
    for k, v in tokens.items():
        data.update({k: v.to_dict() if v else None})
    userinfo = app.authentication_mgr.userinfo.to_dict() if app.authentication_mgr.userinfo else None

    return app.success(tokens=data, userinfo=userinfo, authenticated=app.authentication_mgr.authenticated)


@app.route('/authentication/login', methods=['GET', 'POST'])
def authentication_login():
    if request.method == 'POST':
        is_webview = request.form.get('webview')
        email_address = request.form.get('email')
        password = request.form.get('password')

        if app.authentication_mgr.authenticated:
            return app.error('An account is already signed in.. please logout first')
        elif not email_address or not password:
            return app.error('No email or password parameter provided')

        app.authentication_mgr.email_address = email_address
        app.authentication_mgr.password = password

        try:
            app.authentication_mgr.authenticate()
        except AuthenticationException as e:
            if is_webview:
                return render_template('auth_result.html',
                                       title='Login fail',
                                       result='Login failed',
                                       message='Error: {0}!'.format(str(e)),
                                       link_path='/authentication/login',
                                       link_title='Try again')
            else:
                return app.error('Login failed! Error: {0}'.format(str(e)),
                                 two_factor_required=False)

        except TwoFactorAuthRequired:
            if is_webview:
                return render_template('auth_result.html',
                                       title='Login fail',
                                       result='Login failed, 2FA required',
                                       message='Please click the following link to authenticate via OAUTH',
                                       link_path='/authentication/oauth',
                                       link_title='Login via OAUTH')
            else:
                return app.error('Login failed, 2FA required!',
                                 two_factor_required=True)

        if is_webview:
            return render_template('auth_result.html',
                                   title='Login success',
                                   result='Login succeeded',
                                   message='Welcome {}!'.format(app.logged_in_gamertag()),
                                   link_path='/authentication/logout',
                                   link_title='Logout')
        else:
            return app.success(message='Login success', gamertag=app.logged_in_gamertag())
    elif request.method == 'GET':
        if app.authentication_mgr.authenticated:
            return render_template('auth_result.html',
                                   title='Already signed in',
                                   result='Already signed in',
                                   message='You are already signed in, please logout first!',
                                   link_path='/authentication/logout',
                                   link_title='Logout')
        else:
            return render_template('login.html')


@app.route('/authentication/logout', methods=['GET', 'POST'])
def authentication_logout():
    if request.method == 'POST':
        is_webview = request.form.get('webview')
        username = app.logged_in_gamertag()
        app.reset_authentication()
        if is_webview:
            return render_template('auth_result.html',
                                   title='Logout success',
                                   result='Logout succeeded',
                                   message='Goodbye {0}!'.format(username),
                                   link_path='/authentication/login',
                                   link_title='Login')
        else:
            return app.success(message='Logout succeeded')
    elif request.method == 'GET':
        if app.authentication_mgr.authenticated:
            return render_template('logout.html', username=app.logged_in_gamertag())
        else:
            return render_template('auth_result.html',
                                   title='Logout failed',
                                   result='Logout failed',
                                   message='You are currently not logged in',
                                   link_path='/authentication/login',
                                   link_title='Login')


@app.route('/authentication/authorization_url')
def authentication_get_auth_url():
    return app.success(authorization_url=AuthenticationManager.generate_authorization_url())


@app.route('/authentication/oauth', methods=['GET', 'POST'])
def authentication_oauth():
    if request.method == 'POST':
        is_webview = request.form.get('webview')
        app.reset_authentication()
        redirect_uri = request.form.get('redirect_uri')
        if not redirect_uri:
            return app.error('Please provide redirect_url')

        try:
            access, refresh = AuthenticationManager.parse_redirect_url(redirect_uri)
            app.authentication_mgr.access_token = access
            app.authentication_mgr.refresh_token = refresh
            app.authentication_mgr.authenticate(do_refresh=False)
        except Exception as e:
            if is_webview:
                return render_template('auth_result.html',
                                       title='Login fail',
                                       result='Login failed',
                                       message='Error message: {0}'.format(str(e)),
                                       link_path='/authentication/login',
                                       link_title='Try again')
            else:
                return app.error('Login failed, error: {0}'.format(str(e)))

        if is_webview:
            return render_template('auth_result.html',
                                   title='Login success',
                                   result='Login succeeded',
                                   message='Welcome {}!'.format(app.logged_in_gamertag()),
                                   link_path='/authentication/logout',
                                   link_title='Logout')
        else:
            return app.success(message='Login success', gamertag=app.logged_in_gamertag())
    elif request.method == 'GET':
        if app.authentication_mgr.authenticated:
            return render_template('auth_result.html',
                                   title='Already signed in',
                                   result='Already signed in',
                                   message='You are already signed in, please logout first!',
                                   link_path='/authentication/logout',
                                   link_title='Logout')
        else:
            return render_template('login_oauth.html',
                                   oauth_url=AuthenticationManager.generate_authorization_url())


@app.route('/authentication/refresh')
def authentication_refresh():
    try:
        app.authentication_mgr.authenticate(do_refresh=True)
    except Exception as e:
        return app.error(str(e))

    return app.success()


@app.route('/authentication/load')
def authentication_load_from_disk():
    try:
        app.authentication_mgr.load(TOKENS_FILE)
    except FileNotFoundError as e:
        return app.error('Failed to load tokens from \'{0}\'. Error: {1}'.format(e.filename, e.strerror))

    return app.success()


@app.route('/authentication/store')
def authentication_store_on_disk():
    if not app.authentication_mgr.authenticated:
        return app.error('Sorry, no valid authentication for saving was found')

    try:
        app.authentication_mgr.dump(TOKENS_FILE)
    except Exception as e:
        return app.error('Failed to save tokens to \'{0}\'. Error: {1}'.format(TOKENS_FILE, str(e)))

    return app.success()


@app.route('/devices')
def device_overview():
    discovered = ConsoleWrap.discover().copy()

    liveids = [d.liveid for d in discovered]
    for i, c in enumerate(app.console_cache.values()):
        if c.liveid in liveids:
            # Refresh existing entries
            index = liveids.index(c.liveid)

            if c.device_status != discovered[index].device_status:
                app.console_cache[c.liveid] = ConsoleWrap(discovered[index])
            del discovered[index]
            del liveids[index]
        elif c.liveid not in liveids:
            # Set unresponsive consoles to Unavailable
            app.console_cache[c.liveid].console.device_status = enum.DeviceStatus.Unavailable

    # Extend by new entries
    for d in discovered:
        app.console_cache.update({d.liveid: ConsoleWrap(d)})

    data = {console.liveid: console.status for console in app.console_cache.values()}
    return app.success(devices=data)


@app.route('/devices/<liveid>/poweron')
def poweron(liveid):
    ConsoleWrap.power_on(liveid)
    return app.success()


"""
Require enumerated console
"""


@app.route('/devices/<liveid>')
@console_exists
def device_info(console):
    return app.success(device=console.status)


@app.route('/devices/<liveid>/connect', methods=['GET', 'POST'])
@console_exists
def force_connect(console):
    connect_anonymous = False

    if request.method == 'POST':
        connect_anonymous = True if request.form.get('connect_anonymous') else False

    try:
        state = console.connect(connect_anonymous=connect_anonymous)
    except Exception as e:
        return app.error(str(e))

    if state != enum.ConnectionState.Connected:
        return app.error('Connection failed', connection_state=state.name)

    return app.success(connection_state=state.name)


"""
Require connected console
"""


@app.route('/devices/<liveid>/disconnect')
@console_connected
def disconnect(console):
    console.disconnect()
    return app.success()


@app.route('/devices/<liveid>/poweroff')
@console_connected
def poweroff(console):
    if not console.power_off():
        return app.error("Failed to power off")
    else:
        return app.success()


@app.route('/devices/<liveid>/console_status')
@console_connected
def console_status(console):
    return app.success(console_status=console.console_status)


@app.route('/devices/<liveid>/launch/<app_id>')
@console_connected
def launch_title(console, app_id):
    console.launch_title(app_id)
    return app.success(launched=app_id)


@app.route('/devices/<liveid>/media_status')
@console_connected
def media_status(console):
    return app.success(media_status=console.media_status)


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

    return app.success(**devices)


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

        return app.success(
            device_type=device_config.device_type,
            device_brand=device_config.device_brand,
            device_model=device_config.device_model,
            device_name=device_config.device_name,
            device_id=device_config.device_id,
            buttons=button_links
        )

    return app.error('Device Id \'{0}\' not found'.format(device_id))


@app.route('/devices/<liveid>/ir/<device_id>/<button>')
@console_connected
def infrared_send(console, device_id, button):
    if not console.send_stump_key(device_id, button):
        return app.error('Failed to send button')

    return app.success(sent_key=button, device_id=device_id)


@app.route('/devices/<liveid>/media')
@console_connected
def media_overview(console):
    commands = [cmd.name for cmd in enum.MediaControlCommand]
    return app.success(commands=commands)


@app.route('/devices/<liveid>/media/<command>')
@console_connected
def media_command(console, command):
    try:
        cmd = enum.MediaControlCommand[command]
    except Exception as e:
        return app.error('Invalid command passed, msg: {0}'.format(e))

    console.send_media_command(cmd)
    return app.success()


@app.route('/devices/<liveid>/media/Seek/<seek_position>')
@console_connected
def media_command_seek(console, seek_pos):
    console.send_media_command(enum.MediaControlCommand.Seek, int(seek_pos))
    return app.success()


@app.route('/devices/<liveid>/input')
@console_connected
def input_overview(console):
    buttons = [btn.name for btn in enum.GamePadButton]
    return app.success(buttons=buttons)


@app.route('/devices/<liveid>/input/<button>')
@console_connected
def input_send_button(console, button):
    try:
        btn = enum.GamePadButton[button]
    except Exception as e:
        return app.error('Invalid button passed, msg: {0}'.format(e))

    console.send_gamepad_button(btn)
    return app.success()


@app.route('/devices/<liveid>/stump/headend')
@console_connected
def stump_headend_info(console):
    return app.success(headend_info=console.headend_info.params.dump())


@app.route('/devices/<liveid>/stump/livetv')
@console_connected
def stump_livetv_info(console):
    return app.success(livetv_info=console.livetv_info.params.dump())


@app.route('/devices/<liveid>/stump/tuner_lineups')
@console_connected
def stump_tuner_lineups(console):
    return app.success(tuner_lineups=console.tuner_lineups.params.dump())


@app.route('/devices/<liveid>/text')
@console_connected
def text_overview(console):
    return app.success(text_session_active=console.text_active)


@app.route('/devices/<liveid>/text/<text>')
@console_connected
def text_send(console, text):
    console.send_text(text)
    return app.success()

"""
@app.route('/devices/<liveid>/nano')
@console_connected
def nano_overview(console):
    return app.success(nano_status=console.nano_status)


@app.route('/devices/<liveid>/nano/start')
@console_connected
def nano_start(console):
    console.nano_start()
    return app.success()


@app.route('/devices/<liveid>/nano/stop')
@console_connected
def nano_stop(console):
    console.nano_stop()
    return app.success()
"""


@app.route('/web/title/<title_id>')
@require_authentication
def download_title_info(client, title_id):
    try:
        resp = client.titlehub.get_title_info(title_id, 'image').json()
        return jsonify(resp['titles'][0])
    except KeyError:
        return app.error('Cannot find titles-node json response')
    except IndexError:
        return app.error('No info for requested title not found')
    except Exception as e:
        return app.error('Download of titleinfo failed, error: {0}'.format(e))


@app.route('/versions')
def library_versions():
    import pkg_resources

    versions = {}
    for name in app.smartglass_packetnames:
        try:
            versions[name] = pkg_resources.get_distribution(name).version
        except:
            versions[name] = None

    return app.success(versions=versions)


@app.route('/')
def webroot():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)

    return app.success(endpoints=sorted(routes))
