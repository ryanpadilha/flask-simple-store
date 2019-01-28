import logging

from os import path
from flask import Flask
from flask_login import LoginManager
from flask_uuid import FlaskUUID
from flask_marshmallow import Marshmallow


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = u'Autenticação requerida para acessar a página.'
login_manager.login_message_category = 'info'

flask_uuid = FlaskUUID()
ma = Marshmallow()


def create_app(mode=None):
    """
        Application Factory for Flask

    :param mode:
    :return:
    """
    if mode:
        instance_path = path.join(
            path.abspath(path.dirname(__file__)), "%s_instance" % mode
        )

        app = Flask('brain',
                    instance_path=instance_path,
                    instance_relative_config=True)

        app.config.from_object('brain.default_settings')
        app.config.from_pyfile('config.py')
    else:
        app = Flask('brain',
                    instance_relative_config=False)

        app.config.from_object('brain.default_settings')

    login_manager.init_app(app)
    flask_uuid.init_app(app)
    ma.init_app(app)

    # logging
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    handler.setFormatter(logging.Formatter(app.config['LOGGING_FORMAT']))
    app.logger.addHandler(handler)

    # blueprint section
    from .views.website import website
    app.register_blueprint(website)

    from .views.auth import auth
    app.register_blueprint(auth)

    from .views.manage import manage
    app.register_blueprint(manage)

    from .views.error_handler import error_handler
    app.register_blueprint(error_handler)

    return app
