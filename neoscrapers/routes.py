import logging
import yaml

from openapi_core import create_spec
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters
)

from werkzeug.datastructures import ImmutableMultiDict

from pathlib import Path
from aiohttp.web import (
    Request,
    middleware,
    json_response,
    RouteTableDef,
    Application
)

from neoscrapers import helpers

_LOGGER = logging.getLogger(__name__)

"""OpenApi specs file in ./helpers/api_spec.yaml"""
openapi_spec = create_spec(yaml.load(
    open(
        Path(helpers.__path__[0]) / "api_spec.yaml"
    )
))
validator = RequestValidator(openapi_spec)

"""Routes"""
routes = RouteTableDef()


@routes.get("/user")
async def get_current_user(req: Request):
    res = await validate(req)
    return json_response(res.errors)


def setup_routes(manager, app: Application):
    app.add_routes(routes)


async def validate(req: Request):
    method = req.method.lower()
    cookie = req.cookies or {}

    _LOGGER.info(await parse_query(req.query_string))

    path = {}

    mime_type = req.headers.get('Accept') or \
        req.headers.get('Content-Type')

    query_dict = await parse_query(req.query_string)
    query = ImmutableMultiDict(query_dict.items())

    params = RequestParameters(
        query=query,
        header=req.headers,
        cookie=cookie,
        path=path
    )

    openapi_req = OpenAPIRequest(
        full_url_pattern=req.url,
        method=method,
        parameters=params,
        body=req.text(),
        mimetype=mime_type
    )
    return validator.validate(openapi_req)


async def parse_query(query_string: str):
    # TODO: add decode support

    params = {}

    is_encoded = '+' in query_string or '%' in query_string

    for field in query_string.split('&'):
        k, _, v = field.partition('=')

        """skip if vlaue is empty"""
        if not v:
            continue

        if is_encoded:
            pass

        if k in params:
            old_value = params[k]

            if ',' in v:
                v = v.split(',')

                additional_values = [element for element in v]

                if isinstance(old_value, list):
                    old_value.extend(additional_values)
                else:
                    additional_values.insert(0, old_value)
                    params[k] = additional_values
            else:
                if is_encoded:
                    pass

                if isinstance(old_value, list):
                    old_value.append(v)
                else:
                    params[k] = [old_value, v]
        else:
            if ',' in v:
                v = v.split(',')

                params[k] = [element for element in v]
            elif is_encoded:
                pass
            else:
                params[k] = v

    return params
