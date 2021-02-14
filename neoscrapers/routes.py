import logging
from werkzeug.datastructures import ImmutableMultiDict

from aiohttp import WSMsgType
from aiohttp.web import (
    Request,
    json_response,
    RouteTableDef,
    Application,
    StreamResponse
)
from aiohttp_session import get_session

import magic

from neoscrapers import core
from neoscrapers.users import LoginFailed, UserAlreadyLoggedIn
from neoscrapers import static

_LOGGER = logging.getLogger(__name__)


class USER_ERRORS:
    UNKOWN = {
        "error": {
            "code": 100,
            "msg": "who is this user!?"
        }
    }
    NOT_EXIST = {
        "error": {
            "code": 101,
            "msg": "user does not exist."
        }
    }
    MISSING_FIELDS = {
        "error": {
            "code": 102,
            "msg": "missing fields."
        }
    }
    ALREADY_LOGGED_IN = {
        "error": {
            "code": 103,
            "msg": "already someone logged in."
        }
    }
    NOT_LOGGED_IN = {
        "error": {
            "code": 104,
            "msg": "user not logged in."
        }
    }


class SCRAPER_ERRORS:
    NOT_EXIST = {
        "error": {
            "code": 200,
            "msg": "scraper does not exist."
        }
    }


class OUTPUT_ERRORS:
    NOT_EXIST = {
        "error": {
            "code": 300,
            "msg": "file does not exist."
        }
    }
    INVALID = {
        "error": {
            "code": 301,
            "msg": "invalid filename."
        }
    }

def setup_routes(app: Application):
    """add neoscraper routes to an app.
    
    Args:
        manager (neoscrapers.core.NeoScraper): NeoScraper containing all the other managers.
        app (aiohttp.web.Application): app to add routes to.
    """

    routes = RouteTableDef()

    routes.static(
        '/files',
        static.__path__[0],
        show_index=True,
        follow_symlinks=True,
        append_version=True
    )

    """Get current use if a user is logged in."""
    @routes.get("/user")
    async def get_current_user(req: Request):
        session = await get_session(req)
        usession = core.user_manager.current_session(session)

        if usession is not None:
            return json_response({
                "user": {
                    "username": usession.user.username,
                    "email": usession.user.email,
                    "active_scraper": usession.has_active_scraper
                }
            })

        return json_response(USER_ERRORS.UNKOWN)

    """Log a user in."""
    @routes.post("/user/login")
    async def user_login(req: Request):
        # get current session
        session = await get_session(req)

        """has required fields"""
        if 'email' in req.headers and 'password' in req.headers:
            try:
                email = req.headers.get('email')
                password = req.headers.get('password')
                user = core.user_manager.login(session, email, password)

                return json_response({
                    "user": {
                        "username": user.username,
                        "email": user.email
                    }
                })
            except UserAlreadyLoggedIn:
                return json_response(USER_ERRORS.ALREADY_LOGGED_IN)
            except LoginFailed:
                return json_response(USER_ERRORS.NOT_EXIST)

        """missing fields"""
        return json_response(USER_ERRORS.MISSING_FIELDS)

    @routes.get("/user/logout")
    async def user_logout(req: Request):
        session = await get_session(req)

        core.user_manager.logout(session)

        return json_response({
            "status": "ok"
        })

    @routes.get("/scrapers/list")
    async def scraper_list(req: Request):
        session = await get_session(req)

        if core.user_manager.current_session(session) is not None:
            return json_response({
                "scraper_list": core.scraper_manager.scraper_names()
            })

        return json_response(USER_ERRORS.NOT_LOGGED_IN)

    @routes.post("/scrapers/start")
    async def start_scraper(req: Request):
        session = await get_session(req)
        usession = core.user_manager.current_session(session)

        if usession is not None:
            name = req.headers.get("scraper_name")
            if name and core.scraper_manager.scrapers.get(name):
                scraper = core.scraper_manager.scrapers.get(name)()
                await usession.start_scraper(scraper)

                return json_response({
                    "scraper": scraper.name
                })

            return json_response(SCRAPER_ERRORS.NOT_EXIST)

        return json_response(USER_ERRORS.NOT_LOGGED_IN)

    @routes.get("/output/{filename}")
    async def download_output(req: Request):
        session = await get_session(req)

        if core.user_manager.current_session(session) is None:
            return json_response(USER_ERRORS.NOT_LOGGED_IN)

        if 'filename' in req.match_info:
            filename: str = req.match_info.get("filename")

            if filename.find("/") == -1 and filename.find("\\") == -1:
                path = core.output_manager.output_root / filename

                _LOGGER.info(path)

                if path.exists() and path.is_file():
                    mime = magic.from_file(str(path), mime=True)
                    _LOGGER.info(f"uploading: {filename} {mime}")

                    resp = StreamResponse(headers={'Content-Type': mime})
                    await resp.prepare(req)

                    with path.open('rb') as file:
                        for line in file.readlines():
                            await resp.write(line)

                    await resp.write_eof()
                    return resp

                return json_response(OUTPUT_ERRORS.NOT_EXIST)

            return json_response(OUTPUT_ERRORS.INVALID)

    @routes.get("/ws")
    async def socket_server(req: Request):
        session = await get_session(req)
        usession = core.user_manager.current_session(session)

        if usession is None:
            return json_response(USER_ERRORS.NOT_LOGGED_IN)

        _LOGGER.info("starting websocket")

        ws = await usession.new_socket(req)

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # dict = json.loads(msg.data)
                pass
            elif msg.type == WSMsgType.ERROR:
                _LOGGER.exception(
                    f"socket closed with exception: {ws.exception()}"
                )

        usession.rm_socket(ws)
        return ws

    app.add_routes(routes)
