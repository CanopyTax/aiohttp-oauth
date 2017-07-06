# aiohttp-oauth

OAuth middleware for your aiohttp app. Allows you to require logging in to
an OAuth app in order to get to your app.


## Installation

```bash
pip install aiohttp_oauth
```

## Usage

Currently, only GitHub is supported.

First, you need to create a GitHub app. The callback url is
your domain + `/auth/oauth_callback`


### Basics
During the registration of your aiohttp app, just call the 
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

### Configuring Cookies

If you would like to configure the cookies that this sets for your users,
you can do that by setting `cookie_key` and `cookie_name`.

Example:
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


### Custom OAuth Handler
You can create your own custom OAuth handler. It must implement the interface
of `aiohttp_oauth.auth.OauthHandler`.
Instantiate the object, and pass it into `add_auth_middleware` as the `oauth_handler`
parameter.

### Advanced

This middleware requires aiohttp_session middleware. 
The `add_oauth_middleware` method adds that for you. If you would instead
like to add it yourself, you can add the githubauth middleware yourself.

Example:
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

Pull requests are welcome.
After cloning the repo you can run `python setup.py develop` to get
Python to always point to your development version of the library.
Now start your aiohttp server and you are in business.
