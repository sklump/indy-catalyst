"""Connection handling admin routes."""

import json

from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from marshmallow import fields, Schema

from .manager import CredentialManager
from .messages.inner.credential_preview import (
    AttributePreview,
    CredentialPreview,
    CredentialPreviewSchema
)
from .models.credential_exchange import (
    V10CredentialExchange,
    V10CredentialExchangeSchema
)

from ...connections.models.connection_record import ConnectionRecord

from ....holder.base import BaseHolder
from ....storage.error import StorageNotFoundError


class V10CredentialProposalRequestSchema(Schema):
    """Request schema for sending a credential proposal admin message."""

    connection_id = fields.Str(required=True)
    credential_definition_id = fields.Str(required=True)
    comment = fields.Str(required=False, default="")
    credential_proposal = fields.Nested(CredentialPreviewSchema, required=True)
    cred_def_id = fields.Str(required=True)


class V10CredentialProposalResultSchema(Schema):
    """Result schema for sending a credential proposal admin message."""

    credential_proposal = fields.Dict()  # TODO: what goes here?


class V10CredentialOfferRequestSchema(Schema):
    """Request schema for sending a credential offer admin message."""

    connection_id = fields.Str(required=True)
    credential_definition_id = fields.Str(required=True)
    auto_issue = fields.Bool(required=False, default=False)
    comment = fields.Str(required=False, default="")
    credential_preview = fields.Dict(required=True)


class V10CredentialOfferResultSchema(Schema):
    """Result schema for sending a credential offer admin message."""

    credential_proposal = fields.Dict()  # TODO: what goes here?


class V10CredentialRequestResultSchema(Schema):
    """Result schema for sending a credential request admin message."""

    credential_id = fields.Str()


class V10CredentialIssueRequestSchema(Schema):
    """Request schema for sending a credential issue admin message."""

    comments = fields.Str(required=False, default="")
    credential_values = fields.Dict(required=True)


class V10CredentialIssueResultSchema(Schema):
    """Result schema for sending a credential issue admin message."""

    credential_id = fields.Str()


class V10CredentialExchangeListSchema(Schema):
    """Result schema for a credential exchange query."""

    results = fields.List(fields.Nested(V10CredentialExchangeSchema))


class V10CredentialSchema(Schema):
    """Result schema for a credential query."""

    # properties undefined


class V10CredentialListSchema(Schema):
    """Result schema for a credential query."""

    results = fields.List(fields.Nested(V10CredentialSchema))


@docs(tags=["v1.0 credentials"], summary="Fetch a credential from wallet by id")
@response_schema(V10CredentialSchema(), 200)
async def credentials_get(request: web.BaseRequest):
    """
    Request handler for searching connection records.

    Args:
        request: aiohttp request object

    Returns:
        The connection list response

    """
    context = request.app["request_context"]

    credential_id = request.match_info["id"]

    holder: BaseHolder = await context.inject(BaseHolder)
    credential = await holder.get_credential(credential_id)

    return web.json_response(credential)


@docs(
    tags=["v1.0 credentials"],
    parameters=[
        {
            "name": "start",
            "in": "query",
            "schema": {"type": "string"},
            "required": False,
        },
        {
            "name": "count",
            "in": "query",
            "schema": {"type": "string"},
            "required": False,
        },
        {"name": "wql", "in": "query", "schema": {"type": "string"}, "required": False},
    ],
    summary="Fetch credentials from wallet",
)
@response_schema(V10CredentialListSchema(), 200)
async def credentials_list(request: web.BaseRequest):
    """
    Request handler for searching connection records.

    Args:
        request: aiohttp request object

    Returns:
        The connection list response

    """
    context = request.app["request_context"]

    start = request.query.get("start")
    count = request.query.get("count")

    # url encoded json wql
    encoded_wql = request.query.get("wql") or "{}"
    wql = json.loads(encoded_wql)

    # defaults
    start = int(start) if isinstance(start, str) else 0
    count = int(count) if isinstance(count, str) else 10

    holder: BaseHolder = await context.inject(BaseHolder)
    credentials = await holder.get_credentials(start, count, wql)

    return web.json_response({"results": credentials})


@docs(
    tags=["v1.0 credential_exchange"],
    summary="Fetch all credential exchange records"
)
@response_schema(V10CredentialExchangeListSchema(), 200)
async def credential_exchange_list(request: web.BaseRequest):
    """
    Request handler for searching connection records.

    Args:
        request: aiohttp request object

    Returns:
        The connection list response

    """
    context = request.app["request_context"]
    tag_filter = {}
    for param_name in (
        "connection_id",
        "initiator",
        "state",
        "credential_definition_id",
        "schema_id",
    ):
        if param_name in request.query and request.query[param_name] != "":
            tag_filter[param_name] = request.query[param_name]
    records = await V10CredentialExchange.query(context, tag_filter)
    return web.json_response({"results": [record.serialize() for record in records]})


@docs(
    tags=["v1.0 credential_exchange"],
    summary="Fetch a single credential exchange record"
)
@response_schema(V10CredentialExchangeSchema(), 200)
async def credential_exchange_retrieve(request: web.BaseRequest):
    """
    Request handler for fetching a single connection record.

    Args:
        request: aiohttp request object

    Returns:
        The connection record response

    """
    context = request.app["request_context"]
    credential_exchange_id = request.match_info["id"]
    try:
        record = await V10CredentialExchange.retrieve_by_id(
            context, credential_exchange_id
        )
    except StorageNotFoundError:
        return web.HTTPNotFound()
    return web.json_response(record.serialize())


@docs(tags=["v1.0 credential_exchange"], summary="Sends a credential proposal")
@request_schema(V10CredentialProposalRequestSchema())
@response_schema(V10CredentialProposalResultSchema(), 200)
async def credential_exchange_send_proposal(request: web.BaseRequest):
    """
    Request handler for sending a credential proposal.

    Args:
        request: aiohttp request object

    Returns:
        The credential proposal details.

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    body = await request.json()

    connection_id = body.get("connection_id")
    credential_definition_id = body.get("credential_definition_id")
    comment = body.get("comment")
    credential_preview_raw = body.get("credential_proposal")
    if (isinstance(credential_preview_raw, dict)
            and isinstance(credential_preview_raw.get('attributes', None), list)):
        credential_preview = CredentialPreview(
            attributes=[
                AttributePreview(
                    name=attr_preview['name'],
                    value=attr_preview['value'],
                    mime_type=attr_preview.get('mime_type', None)
                ) for attr_preview in credential_preview_raw['attributes']
            ]
        )
    else:
        raise web.HTTPBadRequest(
            reason='credential_proposal must be a dict mapping "attributes" to '
            + 'list of dicts [{"name": ..., "mime-type": ..., "value": ...}, ...], '
            + 'one dict per attribute.')

    if not credential_preview:
        raise web.HTTPBadRequest(
            reason="credential_proposal must be provided."
        )

    credential_manager = CredentialManager(context)

    raise web.HTTPBadRequest('Connection ID: {}'.format(connection_id))
    connection_record = await ConnectionRecord.retrieve_by_id(context, connection_id)

    if not connection_record.is_active:
        return web.HTTPForbidden()

    (
        credential_exchange_record,
        credential_proposal_message,
    ) = await credential_manager.create_proposal(
        connection_id,
        comment=comment,
        credential_preview=credential_preview,
        credential_definition_id=credential_definition_id
    )

    await outbound_handler(credential_proposal_message, connection_id=connection_id)

    return web.json_response(credential_exchange_record.serialize())


@docs(
    tags=["v1.0 credential_exchange"],
    summary="Sends a credential offer not in reference to any proposal"
)
@request_schema(V10CredentialOfferRequestSchema())
@response_schema(V10CredentialOfferResultSchema(), 200)
async def credential_exchange_send_free_offer(request: web.BaseRequest):
    """
    Request handler for sending a free credential offer.

    A free credential offer is one not having any corresponding proposal
    (issuer initiates).

    Args:
        request: aiohttp request object

    Returns:
        The credential offer details.

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    body = await request.json()

    connection_id = body.get("connection_id")
    credential_definition_id = body.get("credential_definition_id")
    auto_issue = body.get("auto_issue")
    comment = body.get("comment", None)
    cred_preview_raw = body.get("credential_preview")
    credential_preview = None
    if isinstance(cred_preview_raw, dict):
        # default to text/plain attrs on dict of name/value pairs
        credential_preview = CredentialPreview(
            AttributePreview.list_plain(cred_preview_raw)
        )
    elif isinstance(cred_preview_raw, (list, tuple)):
        credential_preview = CredentialPreview([
            AttributePreview(
                name=attr_preview['name'],
                value=attr_preview['value'],
                mime_type=attr_preview.get('mime_type', None)
            ) for attr_preview in cred_preview_raw
        ])
    else:
        raise web.HTTPBadRequest(
            reason="Credential preview must be dict for all text/plain attributes or "
            + "list of dicts [{'name': ..., 'mime_type': ..., 'value': ...}, ...], "
            + "one dict per attribute.")

    if auto_issue and not credential_preview:
        raise web.HTTPBadRequest(
            reason="If auto_issue is set to"
            + " true then credential_preview must also be provided."
        )

    credential_manager = CredentialManager(context)

    connection_record = await ConnectionRecord.retrieve_by_id(context, connection_id)

    if not connection_record.is_active:
        return web.HTTPForbidden()

    credential_exchange_record = V10CredentialExchange(
        connection_id=connection_id,
        initiator=V10CredentialExchange.INITIATOR_SELF,
        credential_definition_id=credential_definition_id,
        auto_issue=auto_issue,
        credential_preview=credential_preview)

    (
        credential_exchange_record,
        credential_offer_message,
    ) = await credential_manager.create_offer(
        credential_exchange_record, connection_record, comment=comment
    )

    await outbound_handler(credential_offer_message, connection_id=connection_id)

    return web.json_response(credential_exchange_record.serialize())


@docs(
    tags=["v1.0 credential_exchange"],
    summary="Sends a credential offer to a proposal"
)
@response_schema(V10CredentialOfferResultSchema(), 200)
async def credential_exchange_send_bound_offer(request: web.BaseRequest):
    """
    Request handler for sending a credential offer to proposal.

    Args:
        request: aiohttp request object

    Returns:
        The credential offer details.

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    credential_exchange_id = request.match_info["id"]
    cred_exch_record = await V10CredentialExchange.retrieve_by_id(
        context, credential_exchange_id
    )
    assert (
        cred_exch_record.state == V10CredentialExchange.STATE_PROPOSAL_RECEIVED
    )

    connection_id = cred_exch_record.connection_id
    connection_record = await ConnectionRecord.retrieve_by_id(context, connection_id)
    if not connection_record.is_active:
        return web.HTTPForbidden()

    credential_manager = CredentialManager(context)

    (
        cred_exch_record,
        credential_offer_message,
    ) = await credential_manager.create_offer(
        cred_exch_record, comment=None
    )

    await outbound_handler(credential_offer_message, connection_id=connection_id)

    return web.json_response(cred_exch_record.serialize())


@docs(tags=["v1.0 credential_exchange"], summary="Sends a credential request")
@response_schema(V10CredentialRequestResultSchema(), 200)
async def credential_exchange_send_request(request: web.BaseRequest):
    """
    Request handler for sending a credential request.

    Args:
        request: aiohttp request object

    Returns:
        The credential request details.

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    credential_exchange_id = request.match_info["id"]
    cred_exch_record = await V10CredentialExchange.retrieve_by_id(
        context, credential_exchange_id
    )
    connection_id = cred_exch_record.connection_id

    assert cred_exch_record.state == V10CredentialExchange.STATE_OFFER_RECEIVED

    credential_manager = CredentialManager(context)

    connection_record = await ConnectionRecord.retrieve_by_id(context, connection_id)

    if not connection_record.is_active:
        return web.HTTPForbidden()

    (
        cred_exch_record,
        credential_request_message,
    ) = await credential_manager.create_request(
        cred_exch_record,
        connection_record
    )

    await outbound_handler(credential_request_message, connection_id=connection_id)
    return web.json_response(cred_exch_record.serialize())


@docs(tags=["v1.0 credential_exchange"], summary="Sends a credential")
@request_schema(V10CredentialIssueRequestSchema())
@response_schema(V10CredentialIssueResultSchema(), 200)
async def credential_exchange_issue(request: web.BaseRequest):
    """
    Request handler for sending a credential.

    Args:
        request: aiohttp request object

    Returns:
        The credential details.

    """
    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    body = await request.json()
    comment = body.get("comment")
    credential_values = body["credential_values"]

    credential_exchange_id = request.match_info["id"]
    cred_exch_record = await V10CredentialExchange.retrieve_by_id(
        context, credential_exchange_id
    )
    connection_id = cred_exch_record.connection_id

    assert cred_exch_record.state == V10CredentialExchange.STATE_REQUEST_RECEIVED

    credential_manager = CredentialManager(context)

    connection_record = await ConnectionRecord.retrieve_by_id(context, connection_id)
    if not connection_record.is_active:
        return web.HTTPForbidden()

    (
        cred_exch_record,
        credential_issue_message,
    ) = await credential_manager.issue_credential(
        cred_exch_record,
        comment=comment,
        credential_values=credential_values
    )

    await outbound_handler(credential_issue_message, connection_id=connection_id)
    return web.json_response(cred_exch_record.serialize())


@docs(
    tags=["v1.0 credential_exchange"],
    summary="Remove an existing credential exchange record",
)
async def credential_exchange_remove(request: web.BaseRequest):
    """
    Request handler for removing a credential exchange record.

    Args:
        request: aiohttp request object
    """
    context = request.app["request_context"]
    credential_exchange_id = request.match_info["id"]
    try:
        credential_exchange_id = request.match_info["id"]
        credential_exchange_record = await V10CredentialExchange.retrieve_by_id(
            context, credential_exchange_id
        )
    except StorageNotFoundError:
        return web.HTTPNotFound()
    await credential_exchange_record.delete_record(context)
    return web.HTTPOk()


async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [
            web.get("/v1.0/credential/{id}", credentials_get),
            web.get("/v1.0/credentials", credentials_list),
            web.get("/v1.0/credential_exchange", credential_exchange_list),
            web.get("/v1.0/credential_exchange/{id}", credential_exchange_retrieve),
            web.post(
                "/v1.0/credential_exchange/send-proposal",
                credential_exchange_send_proposal
            ),
            web.post(
                "/v1.0/credential_exchange/send-offer",
                credential_exchange_send_free_offer
            ),
            web.post(
                "/v1.0/credential_exchange/{id}/send-offer",
                credential_exchange_send_bound_offer
            ),
            web.post(
                "/v1.0/credential_exchange/{id}/send-request",
                credential_exchange_send_request
            ),
            web.post(
                "/v1.0/credential_exchange/{id}/issue",
                credential_exchange_issue
            ),
            web.post(
                "/v1.0/credential_exchange/{id}/remove",
                credential_exchange_remove
            )
        ]
    )
