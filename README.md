# aiohttp-oauth

Oauth middleware for your aiohttp app. Allows you to require logging in to
an oauth app in order to get to your app.

## installation

```bash
pip install aiohttp_oauth
```

## usage

Currently, only github is supported.

First, you need to create a github app. The callback url is
your domain + `/auth/oauth_callback`


### basic
During registration of your aiohttp app, just call the 
`add_oauth_middleware` and everything will be set up for you.
```python
app = web.Application(loop=loop)
aiohttp_oauth.add_oauth_middleware(
    app,
    github_id='[your github client id]',
    github_secret='[your github secret]',
    github_org='[your github org]'
)
```    

### configure cookies

If you would like to configure the cookies that this sets for your users
you can do that by setting `cookie_key` and `cookie_name`

for example:
```python
import aiohttp_oauth


app = web.Application(loop=loop)
aiogithubauth.add_oauth_middleware(
    app,
    github_id='[your github client id]',
    github_secret='[your github secret]',
    github_org='[your github org]',
    cookie_key='some 32 character string',
    cookie_name='some_cookie_name'
)
```


### Custom Oauth Handler
You can create your own custom oauth handler. It must implement the interface
of aiohttp_oauth.auth.OauthHandler.
Instantiate the object, and pass it into `add_auth_middleware` as the `oauth_handler`
parameter.

### advanced

This middleware requires aiohttp_session middleware. 
The `add_oauth_middleware` method adds that for you. If you would instead
like to add it yourself you can add the githubauth middleware yourself.

For example:
```python
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_oauth import oauth_middleware


app = web.Application(loop=loop, middlewares=[
    session_middleware(
           EncryptedCookieStorage(cookie_key.encode(),
                                  cookie_name=cookie_name,
                                  max_age=7200)),
    oauth_middleware(**kwargs),
    # ... 
])
# now add all your other handlers

```


# Contributing

Pull requests welcome.
After cloning the repo you can run `python setup.py develop` to get
python to always point to your development version of the library.
Now start up your aiohttp server and you're in business.
