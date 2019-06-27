"""A credential preview inner object."""


from typing import Sequence

from marshmallow import fields

from ......models.base import BaseModel, BaseModelSchema
from ...message_types import CREDENTIAL_PREVIEW


class AttributePreview(BaseModel):
    """Class representing a preview of an attibute."""

    class Meta:
        """Attribute preview metadata."""

        schema_class = "AttributePreviewSchema"

    def __init__(
            self,
            *,
            name: str,
            value: str,
            encoding: str = None,
            mime_type: str = None,
            **kwargs):
        """
        Initialize attribute preview object.

        Args:
            name: attribute name
            value: attribute value
            mime_type: MIME type

        """
        super(AttributePreview, self).__init__(**kwargs)
        self.name = name
        self.value = value
        self.encoding = encoding
        self.mime_type = mime_type or 'text/plain'

    @staticmethod
    def list_plain(plain: dict):
        """
        Return a list of `AttributePreview` on MIME type text/plain from names/values.

        Args:
            plain: dict mapping names to values

        Returns:
            AttributePreview on name/values pairs with default MIME type

        """
        return [AttributePreview(name=k, value=plain[k]) for k in plain]


class AttributePreviewSchema(BaseModelSchema):
    """Attribute preview schema."""

    class Meta:
        """Attribute preview schema metadata."""

        model_class = AttributePreview

    name = fields.Str(required=True)
    mime_type = fields.Str(
        default='text/plain',
        missing='text/plain',
        data_key='mime-type'
    )
    encoding = fields.Str(required=False)
    value = fields.Str(required=True)


class CredentialPreview(BaseModel):
    """Class representing a credential preview inner object."""

    class Meta:
        """Credential preview metadata."""

        schema_class = "CredentialPreviewSchema"
        message_type = CREDENTIAL_PREVIEW

    def __init__(
            self,
            *,
            attributes: Sequence[AttributePreview] = None,
            **kwargs):
        """
        Initialize credential preview object.

        Args:
            attributes (list): list of attribute preview dicts; e.g., [
                {
                    'name': 'attribute_name',
                    'mime-type': 'text/plain',
                    'value': 'value'
                }
            ]

        """
        super(CredentialPreview, self).__init__(**kwargs)
        self.attributes = list(attributes) if attributes else []

    @property
    def type(self):
        """Accessor for message type."""
        return CredentialPreview.message_type

    def attr_dict(self):
        """Return name:value pair per attribute."""
        return {attr.name: attr.value for attr in self.attributes}

    def mime_type_dict(self):
        """Return name:MIME-type pair per attribute."""
        return {attr.name: attr.mime_type for attr in self.attributes}


class CredentialPreviewSchema(BaseModelSchema):
    """Credential preview schema."""

    class Meta:
        """Credential preview schema metadata."""

        model_class = CredentialPreview

    _type = fields.Str(data_key="@type", dump_only=True, required=False)
    attributes = fields.Nested(
        AttributePreviewSchema,
        many=True,
        required=True,
        data_key='attributes'
    )
