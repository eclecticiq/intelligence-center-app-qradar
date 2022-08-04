"""EclecticIQ app."""
# Licensed Materials - Property of IBM
# 5725I71-CC011829
# (C) Copyright IBM Corp. 2015, 2020. All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
import secrets

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from qpylib import qpylib
from qpylib.encdec import EncryptionError

from app.cipher import Cipher
from app.constants.general import SECRET_KEY, SESSION_COOKIE_NAME, SESSION_ID, SHARED
from app.init import initialize_services
from app.routes import api

# Flask application factory.


def create_app():
    """Create app.

    :return: flask instance
    :rtype: Flask
    """
    # Create a Flask instance.
    qflask = Flask(__name__)

    # add csrf protection
    csrf = CSRFProtect()
    csrf.init_app(qflask)

    # Retrieve QRadar app id.
    qradar_app_id = qpylib.get_app_id()

    # Create unique session cookie name for this app.
    qflask.config[SESSION_COOKIE_NAME.upper()] = SESSION_ID.format(qradar_app_id)

    secret_key = ""  # nosec
    try:
        # Read in secret key
        secret_key = Cipher(SECRET_KEY, SHARED).decrypt()
    except EncryptionError:
        # If secret key file doesn't exist/fail to decrypt it,
        # generate a new random password for it and encrypt it
        secret_key = secrets.token_urlsafe(64)
        # Store in encrypted store
        Cipher(SECRET_KEY, SHARED).encrypt(secret_key)

    qflask.config[SECRET_KEY.upper()] = secret_key

    # Hide server details in endpoint responses.
    # pylint: disable=unused-variable
    @qflask.after_request
    def obscure_server_header(resp):
        resp.headers["Server"] = f"QRadar App {qradar_app_id}"
        return resp

    # Register q_url_for function for use with Jinja2 templates.
    qflask.add_template_global(qpylib.q_url_for, "q_url_for")

    # Initialize logging.
    qpylib.create_log()

    # To enable app health checking, the QRadar App Framework
    # requires every Flask app to define a /debug endpoint.
    # The endpoint function should contain a trivial implementation
    # that returns a simple confirmation response message.
    @qflask.route("/debug")
    def debug():
        return "Pong!"

    # Import additional endpoints.
    # For more information see:
    # https://flask.palletsprojects.com/en/1.1.x/tutorial/views

    qflask.register_blueprint(api.eiq)

    return qflask


scheduler, _logger = initialize_services()
