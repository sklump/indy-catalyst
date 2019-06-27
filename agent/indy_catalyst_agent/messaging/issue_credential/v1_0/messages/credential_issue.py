"""A credential content message."""


from typing import Sequence

from marshmallow import fields

from .....models.attach_decorator import AttachDecorator, AttachDecoratorSchema
from ....agent_message import AgentMessage, AgentMessageSchema
from ..message_types import CREDENTIAL_ISSUE


HANDLER_CLASS = (
    "indy_catalyst_agent.messaging.credentials.v1_0.handlers."
    + "credential_issue_handler.CredentialIssueHandler"
)


class CredentialIssue(AgentMessage):
    """Class representing a credential."""

    class Meta:
        """Credential metadata."""

        handler_class = HANDLER_CLASS
        schema_class = "CredentialIssueSchema"
        message_type = CREDENTIAL_ISSUE

    def __init__(
        self,
        *,
        comment: str = None,
        credentials_attach: Sequence[AttachDecorator] = None,
        **kwargs
    ):
        """
        Initialize credential issue object.

        Args:
            comment: optional comment
            credentials_attach: credentials attachments

        """
        super(CredentialIssue, self).__init__(**kwargs)
        self.comment = comment
        self.credentials_attach = list(credentials_attach) if credentials_attach else []

    def indy_credential(self, index: int = 0):
        """
        Retrieve and decode indy credential from attachment.

        Args:
            index: ordinal in attachment list to decode and return
                (typically, list has length 1)

        """
        return self.credentials_attach[index].indy_dict


class CredentialIssueSchema(AgentMessageSchema):
    """Credential schema."""

    class Meta:
        """Credential schema metadata."""

        model_class = CredentialIssue

    comment = fields.Str(required=False)
    credentials_attach = fields.Nested(
        AttachDecoratorSchema,
        required=True,
        many=True,
        data_key='credentials~attach'
    )
