from reviewer_stk_ai.src.exceptions.integration_error import IntegrationError


def retry_if_integration_error(exception):
    """Return True if we should retry (in this case when it's an IntegrationError), False otherwise"""
    return isinstance(exception, IntegrationError)
