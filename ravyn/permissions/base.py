from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from lilya.compat import is_async_callable
from typing_extensions import Annotated, Doc

from ravyn.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from ravyn.requests import Request
    from ravyn.types import APIGateHandler

SAFE_METHODS: tuple[str, ...] = ("GET", "HEAD", "OPTIONS")


async def maybe_awaitable(func: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
    """
    Executes a function that might be synchronous or asynchronous. Awaits the result
    if the function is a coroutine function.

    Args:
        func: The callable to execute (e.g., a permission's `has_permission` method).
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        The boolean result of the function call.
    """
    if is_async_callable(func):
        return cast(bool, await func(*args, **kwargs))
    return cast(bool, func(*args, **kwargs))


class BaseOperationHolder:
    """
    Base class providing operator overloading magic methods (`&`, `|`, `~`)
    to allow the composition of permissions (e.g., `Perm1 & Perm2`).
    """

    def __and__(self, other: Any) -> "OperandHolder":
        """Handles P1 & P2."""
        return OperandHolder(AND, self, other)

    def __or__(self, other: "Any") -> "OperandHolder":
        """Handles P1 | P2."""
        return OperandHolder(OR, self, other)

    def __rand__(self, other: Any) -> "OperandHolder":
        """Handles P2 & P1 (reflected AND)."""
        return OperandHolder(AND, other, self)

    def __ror__(self, other: "BasePermission") -> "OperandHolder":
        """Handles P2 | P1 (reflected OR)."""
        return OperandHolder(OR, other, self)  # type: ignore

    def __invert__(self) -> "SingleOperand":
        """Handles ~P1 (NOT)."""
        return SingleOperand(NOT, self)  # type: ignore

    def __xor__(self, other: Any) -> "OperandHolder":
        """Handles P1 ^ P2 (Logical XOR)."""
        return OperandHolder(XOR, self, other)

    def __rxor__(self, other: Any) -> "OperandHolder":
        """Handles P2 ^ P1 (Reflected XOR)."""
        return OperandHolder(XOR, other, self)

    def __sub__(self, other: Any) -> "OperandHolder":
        """Handles P1 - P2 (Used for NOR, typically P1 - P2 is NOT (P1 OR P2))."""
        # This is a common, non-standard mapping for NOT(OR) or NOT(AND)
        # Assuming P1 - P2 means NOT(P1 OR P2) (NOR)
        return OperandHolder(NOR, self, other)

    def __rsub__(self, other: Any) -> "OperandHolder":
        """Handles P2 - P1 (Reflected subtraction, used for NOR composition)."""
        # Assuming P2 - P1 means NOT(P2 OR P1) (NOR)
        return OperandHolder(NOR, other, self)


class SingleOperand(BaseOperationHolder):
    """
    A callable wrapper for single-operand logical operations (like NOT).

    When called, it instantiates the inner permission and the operator class.
    """

    def __init__(self, operator_class: type["NOT"], op1_class: type[BaseOperationHolder]) -> None:
        """
        Args:
            operator_class: The logical operator class (e.g., NOT).
            op1_class: The class of the permission to be operated on.
        """
        self.operator_class: type["NOT"] = operator_class
        self.op1_class: type[BaseOperationHolder] = op1_class

    def __call__(self, *args: Any, **kwargs: Any) -> "NOT":
        """Instantiates the permission and wraps it in the NOT operator."""
        op1: BasePermission = self.op1_class(*args, **kwargs)  # type: ignore
        return self.operator_class(op1)


class OperandHolder(BaseOperationHolder):
    """
    A callable wrapper for binary logical operations (like AND, OR, XOR, NOR).

    When called, it instantiates both inner permissions and the operator class.
    """

    def __init__(
        self,
        operator_class: type["AND | OR | NOR | XOR"],
        op1_class: BaseOperationHolder,
        op2_class: BaseOperationHolder,
    ) -> None:
        """
        Args:
            operator_class: The logical operator class (e.g., AND or OR).
            op1_class: The class of the left-hand permission.
            op2_class: The class of the right-hand permission.
        """
        self.operator_class: type[AND | OR | NOR | XOR] = operator_class
        self.op1_class: BaseOperationHolder = op1_class
        self.op2_class: BaseOperationHolder = op2_class

    def __call__(self, *args: Any, **kwargs: Any) -> "AND | OR | XOR | NOR":
        """Instantiates the permissions and wraps them in the AND/OR operator."""
        op1: BasePermission = self.op1_class(*args, **kwargs)  # type: ignore
        op2: BasePermission = self.op2_class(*args, **kwargs)  # type: ignore
        return self.operator_class(op1, op2)


class AND:
    """
    Represents a logical AND operation between two permission instances.
    Implements short-circuiting: if the first permission fails, the second is not checked.
    """

    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        """
        Args:
            op1: The left-hand permission instance.
            op2: The right-hand permission instance.
        """
        self.op1: BasePermission = op1
        self.op2: BasePermission = op2

    async def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if BOTH permissions grant access.

        Returns:
            True if both permissions are granted, False otherwise.
        """
        op1_result: bool = await maybe_awaitable(self.op1.has_permission, request, controller)
        if not op1_result:
            return False
        return await maybe_awaitable(self.op2.has_permission, request, controller)


class OR:
    """
    Represents a logical OR operation between two permission instances.
    Implements short-circuiting: if the first permission succeeds, the second is not checked.
    """

    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        """
        Args:
            op1: The left-hand permission instance.
            op2: The right-hand permission instance.
        """
        self.op1: BasePermission = op1
        self.op2: BasePermission = op2

    async def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if EITHER permission grants access.

        Returns:
            True if either permission is granted, False otherwise.
        """
        op1_result: bool = await maybe_awaitable(self.op1.has_permission, request, controller)
        if op1_result:
            return True
        return await maybe_awaitable(self.op2.has_permission, request, controller)


class NOT:
    """
    Represents a logical NOT operation on a single permission instance.
    """

    def __init__(self, op1: "BasePermission") -> None:
        """
        Args:
            op1: The permission instance to negate.
        """
        self.op1: BasePermission = op1

    async def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if the wrapped permission **denies** access.

        Returns:
            The inverse of the wrapped permission's result.
        """
        result: bool = await maybe_awaitable(self.op1.has_permission, request, controller)
        return not result


class XOR:
    """
    Represents a logical XOR (Exclusive OR) operation between two permission instances.
    Returns True only if exactly one of the permissions is granted.
    """

    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        """
        Args:
            op1: The left-hand permission instance.
            op2: The right-hand permission instance.
        """
        self.op1: BasePermission = op1
        self.op2: BasePermission = op2

    async def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if EXACTLY ONE permission grants access.

        Returns:
            True if (op1 is True AND op2 is False) OR (op1 is False AND op2 is True).
        """
        op1_result: bool = await maybe_awaitable(self.op1.has_permission, request, controller)
        op2_result: bool = await maybe_awaitable(self.op2.has_permission, request, controller)

        # XOR logic: (A or B) and not (A and B)
        return op1_result != op2_result


class NOR:
    """
    Represents a logical NOR (Not OR) operation between two permission instances.
    Returns True only if NEITHER permission is granted.
    """

    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        """
        Args:
            op1: The left-hand permission instance.
            op2: The right-hand permission instance.
        """
        self.op1: BasePermission = op1
        self.op2: BasePermission = op2

    async def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if NEITHER permission grants access.

        Returns:
            True if both permissions are False, False otherwise.
        """
        # Execute both checks
        op1_result: bool = await maybe_awaitable(self.op1.has_permission, request, controller)
        op2_result: bool = await maybe_awaitable(self.op2.has_permission, request, controller)

        # NOR logic: not (A or B)
        return not (op1_result or op2_result)


class BasePermissionMetaclass(BaseOperationHolder, type):
    """
    Metaclass that injects the operator overloading methods (`&`, `|`, `~`)
    directly into the `BasePermission` class, allowing static composition.
    """

    ...


class BasePermission(metaclass=BasePermissionMetaclass):
    """
    The abstract base class for all permissions used by Ravyn.

    Subclasses must inherit from `BasePermission` and override the `has_permission` method
    to implement specific authorization logic.
    """

    def has_permission(
        self,
        request: Annotated[
            "Request",
            Doc(
                """
                The request object being passed through the request.
                """
            ),
        ],
        controller: Annotated[
            "APIGateHandler",
            Doc(
                """
                A [handler](https://ravyn.dev/routing/handlers/) usually
                corresponding the [level](https://ravyn.dev/application/levels/)
                where the permission is placed.
                """
            ),
        ],
    ) -> bool:
        """
        **Mandatory** functionality and entry-point for verifying
        if the resource is available or not.

        The `has_permission` can be both `sync` and `async` depending
        of the needs of application.

        Returns:
            Boolean indicating if has or not permission to access the specific resource.

        **Example with `async`**

        ```python
        from ravyn import BasePermission, Request
        from ravyn.types import APIGateHandler


        class IsProjectAllowed(BasePermission):
            '''
            Permission to validate if has access to a given project
            '''

            async def has_permission(self, request: "Request", controller: "APIGateHandler") -> bool:
                allow_project = request.headers.get("allow_access")
                return bool(allow_project)
        ```

        **Example with `sync`**

        ```python
        from ravyn import BasePermission, Request
        from ravyn.types import APIGateHandler


        class IsProjectAllowed(BasePermission):
            '''
            Permission to validate if has access to a given project
            '''

            def has_permission(self, request: "Request", controller: "APIGateHandler") -> bool:
                allow_project = request.headers.get("allow_access")
                return bool(allow_project)
        ```
        """
        return True


class BaseAbstractUserPermission(BasePermission):
    """
    Abstract Base class for permissions that depend on the existence and status
    of an authenticated user object attached to the request.
    """

    def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        The base check for user permissions: ensures a user object is attached to the request.
        """
        try:
            return hasattr(request, "user")
        except ImproperlyConfigured:
            return False

    @abstractmethod
    def is_user_authenticated(self, request: "Request") -> bool:
        """
        This method must be overridden by subclasses to check the user's
        authentication status.

        Args:
            request: A Lilya 'Connection' instance.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        raise NotImplementedError("is_user_uthenticated() must be implemented.")

    @abstractmethod
    def is_user_staff(self, request: "Request") -> bool:
        """
        This method must be overridden by subclasses to check if the user has
        staff/admin privileges.

        Args:
            request: A Lilya 'Connection' instance.

        Returns:
            bool: True if the user is a staff/admin user, False otherwise.
        """
        raise NotImplementedError("is_user_staff() must be implemented.")


class AllowAny(BasePermission):
    """
    Grants access to any request, regardless of authentication or method.
    """

    def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Returns:
            bool: Always True.
        """
        return True


class DenyAll(BasePermission):
    """
    Denies access to all requests.
    """

    def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Returns:
            bool: Always False.
        """
        return False


class IsAuthenticated(BaseAbstractUserPermission):
    """
    Allows access only if the user is authenticated.
    """

    def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if the request has a user object and if that user is authenticated.

        Args:
            request: A Lilya 'Connection' instance.
            controller: A Ravyn 'APIGateHandler' instance.

        Returns:
            bool: True if the user object exists and `is_user_authenticated` returns True.
        """
        # Ensure user object exists (calls super().has_permission)
        super().has_permission(request, controller)
        return bool(request.user and self.is_user_authenticated(request))


class IsAdminUser(BaseAbstractUserPermission):
    """
    Allows access only if the user is authenticated and has staff/admin privileges.
    """

    def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Checks if the request has a user object and if that user is marked as staff/admin.

        Args:
            request: A Lilya 'Connection' instance.
            controller: A Ravyn 'APIGateHandler' instance.

        Returns:
            bool: True if the user object exists and `is_user_staff` returns True.
        """
        super().has_permission(request, controller)
        return bool(request.user and self.is_user_staff(request))


class IsAuthenticatedOrReadOnly(BaseAbstractUserPermission):
    """
    Allows full access (read/write) if the user is authenticated, or read-only access
    (GET, HEAD, OPTIONS) for anonymous users.
    """

    def has_permission(
        self,
        request: "Request",
        controller: "APIGateHandler",
    ) -> bool:
        """
        Args:
            request: A Lilya 'Connection' instance.
            controller: A Ravyn 'APIGateHandler' instance.

        Returns:
            bool: True if the method is safe (read-only) OR the user is authenticated.
        """
        super().has_permission(request, controller)
        return bool(
            request.method in SAFE_METHODS or request.user and self.is_user_authenticated(request)
        )
