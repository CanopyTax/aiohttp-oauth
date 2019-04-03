from aioauth_client import GoogleClient
import jwt

from .auth import OauthHandler, BadAttemptError


class GSuiteOAuth(OauthHandler):
    def __init__(self, id, secret, redirect_uri, google_org):
        super().__init__()
        self._id = id
        self._secret = secret
        self.org = google_org
        self.redirect_uri = redirect_uri

    def get_state_code(self, request):
        return request.query.get('state', '')

    async def get_oauth_url(self, request, session, state):
        gc = GoogleClient(
            client_id=self._id,
            client_secret=self._secret
        )
        authorize_url = gc.get_authorize_url(
            scope='openid email profile',
            redirect_uri=self.redirect_uri,
            state=state,
            hd=self.org)
        return authorize_url

    async def handle_oauth_callback(self, request, session) -> dict:
        params = request.query

        gc = GoogleClient(
            client_id=self._id,
            client_secret=self._secret
        )
        code = params.get('code')
        if not code:
            raise BadAttemptError("No google code found. It's possible the "
                                  "session timed out while authenticating.")
        otoken, json = await gc.get_access_token(code,
                                                 redirect_uri=self.redirect_uri)
        idt = json['id_token']
        id_token = jwt.decode(idt, verify=False)
        email = id_token.get('email')

        if not (id_token.get('hd') == self.org == email.split('@')[1]):
            raise BadAttemptError("This app does not allow users "
                                  "outside of their organization.")

        info = {'username': email, 'email': email,
                'name': email.split('@')[0].replace('.', ' ').title()}
        return info
