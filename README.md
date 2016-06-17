# aiohttp-github-auth

Github auth middlewear for your aiohttp app


## installation

```
pip install aiogithubauth
```

## usage

First, you need to create a github app. The callback url is
your domain + `/oauth_callback/github`

If you would like to change the callback url, you can do that with the
advanced setup.


### basic
During registration of your aiohttp app, just call the 
`add_github_auth_middleware` and everything will be set up for you.
```
app = web.Application(loop=loop)
    aiogithubauth.add_github_auth_middleware(
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
```
import aiogithubauth


app = web.Application(loop=loop)
aiogithubauth.add_github_auth_middleware(
    app,
    github_id='[your github client id]',
    github_secret='[your github secret]',
    github_org='[your github org]',
    cookie_key='a 16 char string',
    cookie_name='some_cookie_name'
)
```

### advanced

This middleware requires aiohttp_session middleware. 
The `add_github_auth_middleware` method adds that for you. If you would instead
like to add it yourself you can add the githubauth middleware yourself. You
will also need to add the handler for handling oauth callbacks.

For example:
```
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiogithubauth import github_auth_middleware, handle_github_callback


app = web.Application(loop=loop, middlewares=[
    session_middleware(
           EncryptedCookieStorage(cookie_key.encode(),
                                  cookie_name=cookie_name,
                                  max_age=7200)),
    github_auth_middleware(**kwargs),
    # ... 
])

app.router.add_route('GET', '/oauth_callback/github',
                      handle_github_callback)
# now add all your other handlers

```


# Contributing

Pull requests welcome.
After cloning the repo you can run `python setup.py develop` to get
python to always point to your development version of the library.
Now start up your aiohttp server and your in business.