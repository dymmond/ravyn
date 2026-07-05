from lilya import status

from ravyn.utils.enums import HttpMethod

RESERVED_KWARGS = {
    "state",
    "headers",
    "cookies",
    "request",
    "context",
    "socket",
    "data",
    "query",
    "payload",
}
REQUIRED = "required"
IS_DEPENDENCY = "is_dependency"
SKIP_VALIDATION = "skip_validation"

REDIRECT_STATUS_CODES = {
    status.HTTP_301_MOVED_PERMANENTLY,
    status.HTTP_302_FOUND,
    status.HTTP_303_SEE_OTHER,
    status.HTTP_307_TEMPORARY_REDIRECT,
    status.HTTP_308_PERMANENT_REDIRECT,
}

SOCKET = "socket"
DATA = "data"
PAYLOAD = "payload"
REQUEST = "request"
CONTEXT = "context"

AVAILABLE_METHODS = [
    HttpMethod.GET,
    HttpMethod.QUERY,
    HttpMethod.HEAD,
    HttpMethod.PATCH,
    HttpMethod.PUT,
    HttpMethod.POST,
    HttpMethod.DELETE,
    HttpMethod.OPTIONS,
    HttpMethod.TRACE,
]
