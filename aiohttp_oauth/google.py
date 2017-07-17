from aioauth_client import GoogleClient

from .auth import OauthHandler, BadAttemptError


class GoogleOAuth(OauthHandler):
    def __init__(self, id, secret, redirect_uri):
        super().__init__()
        self._id = id
        self._secret = secret
        self.redirect_uri = redirect_uri

    def get_state_code(self, request):
        return request.GET.get('state')

    async def get_oauth_url(self, request, session, state):
        gc = GoogleClient(
            client_id=self._id,
            client_secret=self._secret
        )
        authorize_url = gc.get_authorize_url(
            scope='email profile',
            redirect_uri=self.redirect_uri,
            state=state)
        return authorize_url

    async def handle_oauth_callback(self, request, session) -> dict:
        params = request.GET

        gc = GoogleClient(
            client_id=self._id,
            client_secret=self._secret
        )
        code = params.get('code')
        if not code:
            raise BadAttemptError("No google 'code' parameter found. It's possible the "
                                  "session timed out while authenticating.")
        otoken, _ = await gc.get_access_token(code,
                                              redirect_uri=self.redirect_uri)
        client = GoogleClient(
            # Need a new client, so it includes the new access token
            client_id=self._id,
            client_secret=self._secret,
            access_token=otoken
        )
        user, info = await client.user_info()
        return info
