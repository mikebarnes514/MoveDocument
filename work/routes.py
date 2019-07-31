from flask import request, redirect, session, url_for
from .oauth import client
from . import token


def register(app):

    @app.route('/login')
    def login():
        app.logger.debug('Starting authorization process...')
        return_to = url_for('oauth_authorized', _external=True)
        return client.authorize(return_to)

    @app.route('/oauth_authorized')
    def oauth_authorized():
        next_url = session.pop('next') or url_for('index')
        resp = client.authorized_response()
        if resp is None:
            app.logger.debug('Request to sign in denied')
        else:
            app.logger.debug('Sign in successful')
            token.save(resp['access_token'])
        return redirect(next_url)
