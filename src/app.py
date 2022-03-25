''' Application Entrypoint '''
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.bootstrap import config_bootstrap
from controller import API
from service.users import RevokeAccessRefreshTokens
from settings import FLASK_DEBUG
# from flask_socketio import SocketIO, emit
# from controller.websocket import WebsocketNamespace

if __name__ == "__main__":
    class ReverseProxied(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
            if script_name:
                environ['SCRIPT_NAME'] = script_name
                path_info = environ['PATH_INFO']
                if path_info.startswith(script_name):
                    environ['PATH_INFO'] = path_info[len(script_name):]

            scheme = environ.get('HTTP_X_SCHEME', '')
            if scheme:
                environ['wsgi.url_scheme'] = scheme
            return self.app(environ, start_response)
    APP = Flask(__name__)
    APP.wsgi_app = ReverseProxied(APP.wsgi_app)
    APP.config['JWT_SECRET_KEY'] = 'analytics-users-key'
    JWT = JWTManager(APP)
    APP.config['JWT_BLACKLIST_ENABLED'] = True
    APP.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    # socketio = SocketIO(APP, cors_allowed_origins="*", async_mode=None)
    APP.before_first_request(config_bootstrap)
    CORS(APP)
    API.init_app(APP)
    # socketio.on_namespace(WebsocketNamespace('/notification'))


    @JWT.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        """ Method to check whether token is blacklisted """
        jti = decrypted_token['jti']
        return RevokeAccessRefreshTokens(jti).get()
    APP.run(host='0.0.0.0', debug=FLASK_DEBUG)
