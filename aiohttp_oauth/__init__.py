import uuid
import os

from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp.frozenlist import FrozenList

from .auth import BadAttemptError


async def default_auth_header_handler(request):
    return None


def oauth_middleware(*, auth_callback=None,
                     oauth_url='/auth/oauth_callback',
                     whitelist_handlers=None,
                     oauth_handler=None,
                     auth_header_handler=default_auth_header_handler,
                     **kwargs):
    auth_url = oauth_url
    if oauth_handler is None:
        oauth_handler = _get_auth_handler(url=oauth_url, **kwargs)
    if whitelist_handlers is None:
        whitelist_handlers = []

    async def middleware_factory(app, handler):
        async def handle_oauth_callback(request, session):
            state = oauth_handler.get_state_code(request)
            if session.pop('auth_state_id') != state:
                return web.HTTPForbidden(reason='Bad auth state')

            user = await oauth_handler.handle_oauth_callback(
                request,
                session)

            if auth_callback:
                await auth_callback(user)

            location = session.pop('desired_location')
            session['User'] = user
            return web.HTTPFound(location)

        async def start_authentication(request, session):
            state = str(uuid.uuid4())
            session['auth_state_id'] = state
            session['desired_location'] = request.path_qs

            try:
                redirect_url = await oauth_handler.get_oauth_url(
                    request,
                    session,
                    state
                )
            except BadAttemptError as e:
                return web.HTTPForbidden(reason=str(e))

            return web.HTTPFound(redirect_url)

        async def auth_handler(request):
            """ The auth flow starts here in this method """
            session = await get_session(request)

            if request.headers.get('Authorization'):
                user = await auth_header_handler(request)
                if user is None:
                    return web.HTTPUnauthorized()
            else:
                user = session.get('User')

            if user:  # already authenticated
                request['user'] = user
                return await handler(request)

            final_handler = request.match_info.route.handler
            if final_handler in whitelist_handlers:  # dont need auth
                return await handler(request)

            # Somtimes there is an extra / somewhere, so we strip it out
            path = request.path.replace('//', '/')

            if path == auth_url and \
                    session.get('auth_state_id'):
                """Attempting to authenticate"""
                return await handle_oauth_callback(request, session)

            if request.path.startswith('/api/'):
                return web.HTTPUnauthorized()

            # handle auth!
            return await start_authentication(request, session)

        return auth_handler

    return middleware_factory


def _get_auth_handler(*, url, **kwargs):
    if 'dummy' in kwargs:
        from . import dummy
        return dummy.DummyAuth(url)
    if 'github_id' in kwargs:
        # use github auth
        from . import github
        return github.GithubAuth(id=kwargs['github_id'],
                                 secret=kwargs['github_secret'],
                                 org=kwargs['github_org'])
    if 'google_id' in kwargs:
        from . import google
        return google.GoogleOAuth(
            id=kwargs['google_id'],
            secret=kwargs['google_secret'],
            redirect_uri=kwargs['google_redirect_uri'],
            approved_domains=kwargs['google_approved_domains'])
    if 'gsuite_id' in kwargs:
        from . import gsuite
        return gsuite.GSuiteOAuth(id=kwargs['gsuite_id'],
                                  secret=kwargs['gsuite_secret'],
                                  redirect_uri=kwargs['gsuite_redirect_uri'],
                                  approved_customers=kwargs[
                                      'gsuite_approved_customers'])
    else:
        raise NotImplementedError('Either you didnt provide correct keyword'
                                  ' args or the Auth you desire '
                                  'is not yet implemented')


def add_oauth_middleware(app,
                         cookie_key=None,
                         cookie_name='aiohttp_oauth',
                         cookie_is_secure=False,
                         **kwargs):
    if cookie_key is None:
        print('creating new cookie secret')
        cookie_key = os.urandom(16).hex()

    app._middlewares = FrozenList([
        session_middleware(
            EncryptedCookieStorage(cookie_key.encode(),
                                   cookie_name=cookie_name,
                                   secure=cookie_is_secure,
                                   max_age=7200)),  # two hours
        oauth_middleware(**kwargs)
    ] + list(app._middlewares))
