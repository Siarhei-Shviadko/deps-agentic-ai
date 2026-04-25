from .configured_base_serializer import ConfiguredResponseSerializer

__all__ = [
    "PaginatedMetadataSerializer",
]


class PaginatedMetadataSerializer(ConfiguredResponseSerializer):
    size: int
    total: int
