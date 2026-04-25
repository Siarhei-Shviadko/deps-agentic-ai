from ....configured_base_serializer import ConfiguredResponseSerializer
from ....paginated_metadata import PaginatedMetadataSerializer
from .completion import CompletionSerializer

__all__ = ["CompletionsResponse"]


class CompletionsResponse(ConfiguredResponseSerializer):
    completions: list[CompletionSerializer]
    metadata: PaginatedMetadataSerializer
