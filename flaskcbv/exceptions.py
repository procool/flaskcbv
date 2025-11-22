## Базовые классы исключений FlaskCBV


class FlaskCBVError(Exception):
    """Base exception class for all FlaskCBV errors."""


## Ошибки конфигурации приложения:
class ConfigurationError(FlaskCBVError):
    """Raised when the application is misconfigured.

    Example:
        Raised by CSRF methods when SECRET_KEY is absent
        from the Flask application config.
    """


## Ошибки CSRF-защиты:
class CSRFError(FlaskCBVError):
    """Raised on CSRF token validation failure.

    Covers missing token, expired token, invalid signature,
    and token mismatch between session and form data.
    """
