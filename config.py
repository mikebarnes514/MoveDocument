# General application configuration
DEBUG = False

# Session cookie configuration
SESSION_COOKIE_NAME = 'docketing'
SECRET_KEY = 'docketing'

# Work API related configuration
WORK_CONFIG = {
    'base_url': 'https://imanage.millerjohnson.com',
    'consumer_key': 'docketing',
    'consumer_secret': 'docketing',
    'request_token_params': {
        'scope': 'user'
    }
}
