from ...configured_base_serializer import ConfiguredRequestSerializer

__all__ = ["UpdateConversationRequest"]


class UpdateConversationRequest(ConfiguredRequestSerializer):
    title: str
