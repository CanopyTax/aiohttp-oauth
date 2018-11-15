from aioauth_client import GithubClient

from .auth import OauthHandler, BadAttemptError


class GithubAuth(OauthHandler):
    def __init__(self, id, secret, org):
        super().__init__()
        self._id = id
        self._secret = secret
        self.org = org

    def get_state_code(self, request):
        return request.query.get('state', '')

    async def get_oauth_url(self, request, session, state):
        gh = GithubClient(
            client_id=self._id,
            client_secret=self._secret
        )
        authorize_url = gh.get_authorize_url(
            scope='user:email read:org',
            state=state)
        return authorize_url

    async def handle_oauth_callback(self, request, session) -> dict:
        params = request.query

        gh = GithubClient(
            client_id=self._id,
            client_secret=self._secret
        )
        code = params.get('code')
        if not code:
            raise BadAttemptError("No github code found. It's possible the "
                                  "session timed out while authenticating.")
        otoken, _ = await gh.get_access_token(code)
        gh = GithubClient(
            # Need a new client, so it includes the new access token
            client_id=self._id,
            client_secret=self._secret,
            access_token=otoken
        )
        req = await gh.request('GET', 'user')
        user = await req.json()
        req.close()
        req = await gh.request('GET', 'user/orgs')
        orgs = await req.json()
        req.close()

        for org in orgs:
            if org.get('login') == self.org:
                user['username'] = user.get('login')
                return user

        raise BadAttemptError('User not in correct Org')
