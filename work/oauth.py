from flask_oauthlib.client import OAuth

client = OAuth().remote_app('work',
                            app_key='WORK_CONFIG',
                            authorize_url='/login/oauth2/authorize',
                            access_token_url='/login/oauth2/access_token',
                            request_token_url=None)
