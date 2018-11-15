from .auth import OauthHandler


class DummyAuth(OauthHandler):
    def __init__(self, url):
        super().__init__()
        self._url = url

    def get_state_code(self, request):
        return request.query.get('state', '')


    async def get_oauth_url(self, request, session, state):
        return self._url + '?state={}'.format(state)

    async def handle_oauth_callback(self, request, session) -> dict:
        return {'username': 'admin',
                'email': 'admin@example.com',
                'name': 'Mr. Admin'}
