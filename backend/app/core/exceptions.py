from fastapi import HTTPException, status


class UDMSException(Exception):
    """Base exception for UDMS."""
    def __init__(self, message: str = "An error occurred", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# ─── Auth Exceptions ─────────────────────────────────────────────────────────
class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid username or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": detail, "error_code": "INVALID_CREDENTIALS"},
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(HTTPException):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": detail, "error_code": "TOKEN_EXPIRED"},
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenException(HTTPException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": detail, "error_code": "INVALID_TOKEN"},
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveAccountException(HTTPException):
    def __init__(self, detail: str = "Account is not yet activated. Please verify your email."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": detail, "error_code": "ACCOUNT_INACTIVE"},
        )


class SuspendedAccountException(HTTPException):
    def __init__(self, detail: str = "Your account has been suspended. Contact support."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": detail, "error_code": "ACCOUNT_SUSPENDED"},
        )


class AccountLockedOutException(HTTPException):
    def __init__(self, minutes: int = 15):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": f"Account temporarily locked due to too many failed attempts. Try again in {minutes} minutes.",
                "error_code": "ACCOUNT_LOCKED",
                "retry_after_minutes": minutes,
            },
        )


class OTPExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "OTP has expired. Please request a new one.", "error_code": "OTP_EXPIRED"},
        )


class OTPInvalidException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Invalid OTP. Please check your code and try again.", "error_code": "OTP_INVALID"},
        )


class OTPCooldownException(HTTPException):
    def __init__(self, seconds: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "success": False,
                "message": f"Please wait {seconds} seconds before requesting a new OTP.",
                "error_code": "OTP_COOLDOWN",
                "retry_after_seconds": seconds,
            },
        )


# ─── Authorization Exceptions ─────────────────────────────────────────────────
class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": detail, "error_code": "PERMISSION_DENIED"},
        )


class UnauthenticatedException(HTTPException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": detail, "error_code": "UNAUTHENTICATED"},
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Resource Exceptions ─────────────────────────────────────────────────────
class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Resource", identifier: str = ""):
        msg = f"{resource} not found" + (f": {identifier}" if identifier else "")
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": msg, "error_code": "NOT_FOUND"},
        )


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": detail, "error_code": "CONFLICT"},
        )


class ValidationException(HTTPException):
    def __init__(self, detail: str = "Validation failed", errors: list = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "message": detail,
                "error_code": "VALIDATION_ERROR",
                "errors": errors or [],
            },
        )


# ─── Business Logic Exceptions ────────────────────────────────────────────────
class MealDeadlinePassedException(HTTPException):
    def __init__(self, action: str = "add", meal_type: str = "meal"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": f"Cannot {action} {meal_type} — the deadline has passed.",
                "error_code": "MEAL_DEADLINE_PASSED",
            },
        )


class MealAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "You already have this meal enrolled for today.", "error_code": "MEAL_ALREADY_EXISTS"},
        )


class MealInactiveException(HTTPException):
    def __init__(self, meal_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": f"{meal_type} is currently not available.",
                "error_code": "MEAL_INACTIVE",
            },
        )


class CustomerAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "This student is already a customer.", "error_code": "CUSTOMER_EXISTS"},
        )


class NotACustomerException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "This student is not enrolled as a customer.", "error_code": "NOT_A_CUSTOMER"},
        )


class InsufficientPermissionsException(HTTPException):
    def __init__(self, required_role: str = ""):
        msg = "Insufficient permissions"
        if required_role:
            msg = f"This action requires {required_role} role"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": msg, "error_code": "INSUFFICIENT_PERMISSIONS"},
        )


class RoleChangeNotAllowedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "The Provost role cannot be changed through this interface.",
                "error_code": "ROLE_CHANGE_NOT_ALLOWED",
            },
        )


class UploadTooLargeException(HTTPException):
    def __init__(self, max_mb: int = 5):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"success": False, "message": f"File size exceeds the {max_mb}MB limit.", "error_code": "UPLOAD_TOO_LARGE"},
        )


class InvalidFileTypeException(HTTPException):
    def __init__(self, allowed_types: list = None):
        allowed = ", ".join(allowed_types or []) or "image/jpeg, image/png"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": f"Invalid file type. Allowed: {allowed}", "error_code": "INVALID_FILE_TYPE"},
        )


class ServiceUnavailableException(HTTPException):
    def __init__(self, service: str = "Service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"success": False, "message": f"{service} is temporarily unavailable.", "error_code": "SERVICE_UNAVAILABLE"},
        )
