import logging
import random
import asyncio
import threading

from aiohttp.web import WebSocketResponse, Request
import aiohttp_session

from neoscrapers import data
from neoscrapers.helpers.types import Scraper

_LOGGER = logging.getLogger(__name__)

SESSION_KEY = 'user_session_id'


# TODO: user class
class User:
    def __init__(self, username: str, email: str, password: str):
        """User object

        Args:
            username (str): username
            email (str): email
            password (str): password
        """
        self.username = username
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email
        }


class UserSession:
    def __init__(self, user: User):
        """User session.
        keeps track of websockets and active scrapers to commicate with.

        Args:
            user (neoscrapers.users.User): user of session
        """
        self.user = user
        self.scraper = None
        self._sockets = []
        self._thread = None

    @property
    def has_active_scraper(self):
        if self.scraper is None:
            return False
        return True

    async def start_scraper(self, scraper: Scraper):
        """Start scraper

        Args:
            scraper (neoscrapers.helpers.scraper.Scraper): Scraper to start. e.g. obtained trough scrapermanager.
        """
        self.scraper = scraper
        await self.scraper.progress.subscribe(self._send_value_update)

        await self.scraper.run()

    async def new_socket(self, req) -> WebSocketResponse:
        """Add new socket to session.

        Args:
            req (aiohttp.web.Request): Request to bind the socket to.

        Returns:
            WebSocketResponse: resulting websocket
        """
        new_ws = WebSocketResponse()
        self._sockets.append(new_ws)

        await new_ws.prepare(req)

        if self.scraper is not None:
            await self._send_value_update(self.scraper.progress.value)
        return new_ws

    def rm_socket(self, ws: WebSocketResponse):
        """Remove websocket from session.

        Args:
            ws (aiohttp.web.WebSocketResponse): socket to remove.
        """
        if ws in self._sockets:
            self._sockets.remove(ws)

    async def _send_json_to_sockets(self, data: dict):
        """Send dict to all sockets in this session.

        Args:
            data (dict): data
        """
        await asyncio.gather(
            *(
                ws.send_json(data) for ws in self._sockets
            )
        )

    async def _send_value_update(self, val):
        """Send value update of active scraper.
        sends complete message if val is bigger then 1.

        Args:
            val (float): 0-1
        """
        await self._send_json_to_sockets({
            "type": "active_scraper",
            "data": {
                "name": self.scraper.name,
                "progress": val
            }
        })

        if val >= 1:
            await self._send_complete()

    async def _send_complete(self):
        """Send complete message containing filename for downloading.
        """
        await self._send_json_to_sockets({
            "type": "completed_scraper",
            "data": {
                "name": self.scraper.name,
                "download": self.scraper.output.file
            }
        })

        await self.scraper.progress.unsubscribe(self._send_value_update)
        self.scraper = None


# TODO: usermanager
class UserManager:
    def __init__(self):
        self._sessions = {}

        if not data.config_dict.get('users'):
            data.config_dict['users'] = []

    @property
    def users(self):
        """
        Get a array of User objects.
        """
        list = []

        for u in data.config_dict['users']:
            list.append(User(u['username'], u['email'], u['password']))

        return list

    def login(self, session: aiohttp_session.Session, email: str, password: str) -> User:
        """Log an user in.

        Args:
            session (aiohttp_session.Session): Session to bind UserSession to.
            email (str): Email
            password (str): Passowrd

        Raises:
            UserAlreadyLoggedIn: User already logged in. logout first.
            LoginFailed: login failed. (user does not exist)

        Returns:
            User: Return user object after succesfull login.
        """
        if SESSION_KEY in session and session[SESSION_KEY] in self._sessions:
            raise UserAlreadyLoggedIn

        u = self.get_by_email(email)
        if u is not None and u.password == password:
            self._new_session(session, u)
            _LOGGER.info("A user logged in.")
            return u

        raise LoginFailed

    def logout(self, session: aiohttp_session.Session):
        """Logout user from session.

        Args:
            session (aiohttp_session.Session): session.
        """
        self._del_user_session(session)
        _LOGGER.info("A user logged out.")

    # TODO: finish register function.
    def register(self, username: str, email: str, password: str):
        pass

    def current(self, session: aiohttp_session.Session) -> User:
        """Get current user. NOT current user session.

        Args:
            session (aiohttp_session.Session): session

        Returns:
            User: user in current session. None if no user logged in.
        """
        usession = self._get_user_session(session)

        if usession is not None:
            return usession.user

        return None

    def current_session(self, session: aiohttp_session.Session) -> UserSession:
        """Get current UserSession

        Args:
            session (aiohttp_session.Session): session.

        Returns:
            neoscrapers.users.UserSession: user session.
        """
        return self._get_user_session(session)

    def is_user(self, user: User) -> bool:
        """Check if user exists.

        Args:
            user (neoscrapers.users.User): user to check for.

        Returns:
            bool: result.
        """
        for u in self.users:
            if u.email == user.email:
                return True

        return False

    def get_by_email(self, email: str) -> User:
        """Get user object by email.

        Args:
            email (str): email

        Returns:
            User: user. Is None if user does not exist.
        """
        for u in self.users:
            if u.email.lower() == email.lower():
                return u

        return None

    def _get_user_session(self, session: aiohttp_session.Session) -> UserSession:
        """Get user session from current session.

        Args:
            session (aiohttp_session.Session): session to get UserSession from.

        Returns:
            neoscrapers.users.UserSession: user session.
        """
        if SESSION_KEY in session and session[SESSION_KEY] in self._sessions:
            return self._sessions[session[SESSION_KEY]]

        return None

    def _new_session(self, session: aiohttp_session.Session, user: User) -> UserSession:
        """Create new session. if user already has a open session return None.

        Args:
            session (aiohttp_session.Session): session
            user (User): user

        Returns:
            neoscrapers.users.UserSession: user session
        """
        if not self._user_has_session(user):
            # create new session with random id.
            new_id = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            self._sessions[new_id] = UserSession(user)
            session[SESSION_KEY] = new_id

            _LOGGER.debug(f"New user session: {new_id}")

            return new_id
        else:
            for k in self._sessions:
                if self._sessions[k].user == user and not SESSION_KEY in session:
                    session[SESSION_KEY] = k

    def _user_has_session(self, user: User) -> bool:
        """Check if user already has a running session.

        Args:
            user (User): user.

        Returns:
            bool: result.
        """
        for k in self._sessions:
            if self._sessions[k].user == user:
                return True

        return False

    def _del_user_session(self, session: aiohttp_session.Session):
        """Delete user session.

        Args:
            session (aiohttp_session.Session): session.
        """
        if SESSION_KEY in session and session[SESSION_KEY] in self._sessions:
            _LOGGER.debug(f"Deleting user session: {session[SESSION_KEY]}")

            self._sessions.pop(session[SESSION_KEY])
            session.pop(SESSION_KEY)


class UserAlreadyLoggedIn(Exception):
    pass


class LoginFailed(Exception):
    pass