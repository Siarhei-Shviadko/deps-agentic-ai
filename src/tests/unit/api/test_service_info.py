import pytest

from deps_agentic_ai import constants


class TestServiceInfo:
    endpoint = constants.BASE_API_PREFIX + "/service-info"

    @pytest.mark.asyncio
    async def test_version(self, client):
        response = await client.get(f"{self.endpoint}/version")

        assert response.status_code == 200
