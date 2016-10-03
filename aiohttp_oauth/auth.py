from abc import ABCMeta, abstractmethod
from typing import Dict


class BadAttemptError(Exception):
    """ A bad attempt at auth has occurred"""


class OauthHandler(metaclass=ABCMeta):

    @abstractmethod
    def get_state_code(self, request):
        """Return the "state" security code"""
        pass

    @abstractmethod
    async def get_oauth_url(self, request, session, state):
        """return the url needed for oauth"""
        pass

    @abstractmethod
    async def handle_oauth_callback(self, request, session) -> Dict[str, str]:
        """ handle the oauth call and return the user info
        Make sure to check for proper membership. Return None if
        the user is not authorized, or a """
        pass
