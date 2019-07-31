from flask import session, redirect, request, url_for
from functools import wraps
from .oauth import client


@client.tokengetter
def load(token=None):
    token = session.get('work_token')
    if not token:
        return None
    return token, ''


def save(access_token):
    session['work_token'] = access_token


def required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_exists = load() is not None
        if not token_exists:
            session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
