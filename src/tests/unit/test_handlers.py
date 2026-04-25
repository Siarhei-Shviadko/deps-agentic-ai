from deps_agentic_ai.messaging.handlers import (
    agent_vendor_deleted_handler,
    document_deleted_handler,
    document_type_deleted_handler,
)


def test_agent_vendor_deleted_handler__ok(mock_command_conversation_service, agent_vendor_deleted_event):
    mock_command_conversation_service.delete_with_agent_vendor.return_value = None

    agent_vendor_deleted_handler(agent_vendor_deleted_event)

    mock_command_conversation_service.delete_with_agent_vendor.assert_called_once_with(
        agent_vendor_deleted_event.event.id
    )


def test_document_deleted_handler__ok(mock_command_conversation_service, document_deleted_event):
    mock_command_conversation_service.delete_with_document_relation.return_value = None

    document_deleted_handler(document_deleted_event)

    mock_command_conversation_service.delete_with_document_relation.assert_called_once_with(
        document_deleted_event.event.document_id
    )


def test_document_type_deleted_handler__ok(mock_command_conversation_service, document_type_deleted_event):
    mock_command_conversation_service.delete_with_document_type_relation.return_value = None

    document_type_deleted_handler(document_type_deleted_event)

    mock_command_conversation_service.delete_with_document_type_relation.assert_called_once_with(
        document_type_deleted_event.event.document_type, document_type_deleted_event.event.tenant
    )
