"""Credential request handler."""


from ....base_handler import (
    BaseHandler,
    BaseResponder,
    HandlerException,
    RequestContext
)

from ..manager import CredentialManager
from ..messages.credential_request import CredentialRequest


class CredentialRequestHandler(BaseHandler):
    """Message handler class for credential requests."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """
        Message handler logic for credential requests.

        Args:
            context: request context
            responder: responder callback
        """
        self._logger.debug(f"CredentialRequestHandler called with context {context}")

        assert isinstance(context.message, CredentialRequest)

        self._logger.info(
            "Received credential request: %s", context.message.serialize(as_string=True)
        )

        if not context.connection_active:
            raise HandlerException("No connection established for credential request")

        credential_manager = CredentialManager(context)
        cred_exchange_rec = await credential_manager.receive_request(
            credential_request_message=context.message
        )

        # If auto_issue is enabled, respond immediately
        if cred_exchange_rec.auto_issue:
            (
                cred_exchange_rec,
                credential_issue_message,
            ) = await credential_manager.issue_credential(
                credential_exchange_record=cred_exchange_rec,
                comment=context.message.comment,
                credential_values=cred_exchange_rec.credential_preview.attr_dict()
            )

            await responder.send_reply(credential_issue_message)
