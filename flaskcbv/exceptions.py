## Базовые классы исключений FlaskCBV


class FlaskCBVError(Exception):
    pass


## Ошибки конфигурации приложения:
class ConfigurationError(FlaskCBVError):
    pass


## Ошибки CSRF-защиты:
class CSRFError(FlaskCBVError):
    pass
