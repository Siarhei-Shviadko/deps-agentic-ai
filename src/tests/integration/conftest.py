import pytest

from deps_agentic_ai.domain.model.agent_vendor import IQueryAgentVendorRepository
from deps_agentic_ai.domain.model.conversation import IQueryConversationRepository
from deps_agentic_ai.domain.model.mode import IQueryModeRepository
from deps_agentic_ai.domain.model.tool_set import IQueryToolSetRepository


@pytest.fixture
def query_tool_set_repository(repositories) -> IQueryToolSetRepository:
    return repositories.query_tool_set()


@pytest.fixture
def query_mode_repository(repositories) -> IQueryModeRepository:
    return repositories.query_mode()


@pytest.fixture
def query_agent_vendor_repository(repositories) -> IQueryAgentVendorRepository:
    return repositories.query_agent_vendor()


@pytest.fixture
def query_conversation_repository(repositories) -> IQueryConversationRepository:
    return repositories.query_conversation()
