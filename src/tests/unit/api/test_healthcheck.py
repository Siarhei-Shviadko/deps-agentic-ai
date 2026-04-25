import pytest

from deps_agentic_ai import constants


class TestHealthcheck:
    endpoint = constants.BASE_API_PREFIX

    @pytest.mark.asyncio
    async def test_healthcheck_endpoint_return_200(self, client, postgres_session_mock):
        postgres_session_mock.healthcheck.return_value = ""
        response = await client.get(f"{self.endpoint}/healthcheck")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_healthcheck_endpoint_return_503(self, client, postgres_session_mock):
        postgres_session_mock.healthcheck.side_effect = Exception("Service unavailable")
        response = await client.get(f"{self.endpoint}/healthcheck")

        assert response.status_code == 503
