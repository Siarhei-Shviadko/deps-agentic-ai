__all__ = ["AgenticAiException", "NotFound", "IllegalArgument", "Conflict", "AlreadyExists", "InvariantViolation"]


class AgenticAiException(Exception):
    code = "agentic_ai_exception"


class BusinessException(AgenticAiException):
    code = "business_exception"


class Conflict(AgenticAiException):
    code = "conflict_error"


class NotFound(AgenticAiException):
    code = "not_found_error"


class AlreadyExists(Conflict):
    code = "already_exists_error"


class IllegalArgument(AgenticAiException):
    code = "illegal_argument"


class InvariantViolation(BusinessException):
    code = "invariant_violation"
