from flask import Flask, jsonify, request, render_template, redirect
from http import HTTPStatus
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.api.client import XboxLiveClient
from xbox.rest.scripts import TOKENS_FILE
from .routes import routes

class SmartGlassFlaskApp(Flask):
    def __init__(self, name):
        super(SmartGlassFlaskApp, self).__init__(name)

        self.console_cache = {}
        self.authentication_mgr = AuthenticationManager()
        self._xbl_client = None

        try:
            # Best effort token load & refresh
            self.authentication_mgr.load(TOKENS_FILE)
            self.authentication_mgr.authenticate(do_refresh=True)
        except:
            pass

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

    @property
    def xbl_client(self):
        if self.authentication_mgr.authenticated and not self._xbl_client:
            self._xbl_client = XboxLiveClient(
                userhash=app.authentication_mgr.userinfo.userhash,
                auth_token=app.authentication_mgr.xsts_token.jwt,
                xuid=app.authentication_mgr.userinfo.xuid
            )
        return self._xbl_client

    def logged_in_gamertag(self):
        return self.authentication_mgr.userinfo.gamertag if self.authentication_mgr.userinfo else '<UNKNOWN>'

    def reset_authentication(self):
        self.authentication_mgr = AuthenticationManager()

    def error(self, message, code=HTTPStatus.INTERNAL_SERVER_ERROR, **kwargs):
        ret = {
            'success': False,
            'message': message
        }
        if kwargs:
            ret.update(kwargs)
        return jsonify(ret), code

    def success(self, **kwargs):
        ret = {'success': True}
        if kwargs:
            ret.update(kwargs)
        return jsonify(ret)


app = SmartGlassFlaskApp(__name__)
app.register_blueprint(routes)
