from aioauth_client import GithubClient
import os
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp import web
import urllib

gh_id = None
gh_secret = None
gh_org = None


def github_auth_middleware(*, github_id, github_secret, github_org,
                           whitelist_handlers=None, redirect_handlers=None):
    """ Middleware to do github auth
    :param github_id: github client id
    :param github_secret: github secret
    :param github_org: github organization for which people are authorized
    :param whitelist_handlers: a list of handler methods
        which do not need authorization
    :param redirect_handlers: a list of handler methods
        which will cause an automatic redirect to login to github.
        If empty, all handlers will redirect.
        If provided, all other handlers will cause a 401 istead of a
        redirect to github login

    :return: middleware_factory
    """
    global gh_id, gh_secret, gh_org
    gh_id = github_id
    gh_secret = github_secret
    gh_org = github_org
    whitelist_handlers = whitelist_handlers or []
    redirect_handlers = redirect_handlers or []

    async def middleware_factory(app, handler):

        async def auth_handler(request):
            session = await get_session(request)
            params = urllib.parse.parse_qs(request.query_string)
            user = session.get('User')
            if user:  # already authenticated
                pass
            elif handler in whitelist_handlers:  # dont need authentication
                pass
            elif handler == handle_github_callback and \
                    session.get('github_state'):
                # Attempting to authenticate - let them pass through
                        pass

            elif handler in redirect_handlers or not redirect_handlers:
                gh = GithubClient(
                    client_id=gh_id,
                    client_secret=gh_secret
                )
                state = os.urandom(30).hex()
                authorize_url = gh.get_authorize_url(
                    scope='user:email read:org',
                    state=state)
                session['github_state'] = state
                session['desired_location'] = request.path
                return web.HTTPFound(authorize_url)
            else:
                return web.HTTPUnauthorized()

            return await handler(request)

        return auth_handler

    return middleware_factory


async def handle_github_callback(request):
    params = urllib.parse.parse_qs(request.query_string)
    session = await get_session(request)

    # check conditions
    if (session.get('github_state') !=  # gh state is incorrect
                params.get('state', [None])[0]):
        print('bad state returned')
        """
        Codes are the same, we are in the middle of
        authenticating and things look ok, carry on
        """
        return web.HTTPForbidden()

    gh = GithubClient(
        client_id=gh_id,
        client_secret=gh_secret
    )
    code = params.get('code', [None])[0]
    if not code:
        return web.HTTPNotFound(body=b'Page not found. Its possible the '
                                     b'session timed out while authenting.')
    otoken, _ = await gh.get_access_token(code)
    gh = GithubClient(
        client_id=gh_id,
        client_secret=gh_secret,
        access_token=otoken
    )
    req = await gh.request('GET', 'user')
    user = await req.json()
    req.close()
    req = await gh.request('GET', 'user/orgs')
    orgs = await req.json()
    req.close()

    for org in orgs:
        if org.get('login') == gh_org:

            # swap github_state for user
            session.pop('github_state', None)
            session['User'] = user.get('login')
            location = session.pop('desired_location')
            return web.HTTPFound(location)

    return web.HTTPForbidden()


def add_github_auth_middleware(app,
                               cookie_key=None,
                               cookie_name='aiogithubauth',
                               **kwargs):
    if cookie_key is None:
        print('creating new cookie secret')
        cookie_key = os.urandom(16).hex()

    app._middlewares = [
           session_middleware(
               EncryptedCookieStorage(cookie_key.encode(),
                                      cookie_name=cookie_name,
                                      max_age=7200)),  # two hours
           github_auth_middleware(**kwargs)
           ] + app._middlewares

    app.router.add_route('GET', '/oauth_callback/github',
                         handle_github_callback)
