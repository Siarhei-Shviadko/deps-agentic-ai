import pytest

from deps_agentic_ai import constants


class TestDebug:
    endpoint = constants.BASE_API_PREFIX

    @pytest.mark.asyncio
    async def test_debug_endpoint_return_500(self, client):
        with pytest.raises(ValueError):
            await client.get(f"{self.endpoint}/debug/500")
