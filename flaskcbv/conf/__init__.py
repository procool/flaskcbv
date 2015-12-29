import os, sys

from defaults import DefaultSettings

ENVIRONMENT_VARIABLE = "FLASK_SETTINGS_MODULE"

def import_module(name, package=None):
        """Import a module.

        The 'package' argument is required when performing a relative import. It
        specifies the package to use as the anchor point from which to resolve the
        relative import to an absolute import.

        """
        if name.startswith('.'):
            if not package:
                raise TypeError("relative imports require the 'package' argument")
            level = 0
            for character in name:
                if character != '.':
                    break
                level += 1
            name = _resolve_name(name[level:], package, level)
        __import__(name)
        return sys.modules[name]

class BaseSettings(object):
    """
    Common logic for settings whether set by a module or by the user.
    """
    def __setattr__(self, name, value):
        #if name in ("MEDIA_URL", "STATIC_URL") and value and not value.endswith('/'):
        #    raise ImproperlyConfigured("If set, %s must end with a slash" % name)
        #elif name == "ALLOWED_INCLUDE_ROOTS" and isinstance(value, six.string_types):
        #    raise ValueError("The ALLOWED_INCLUDE_ROOTS setting must be set "
        #        "to a tuple, not a string.")
        object.__setattr__(self, name, value)


class Settings(DefaultSettings, BaseSettings):
    def __init__(self):
        settings_module = os.environ[ENVIRONMENT_VARIABLE]
        if not settings_module: # If it's set but is an empty string.
            raise KeyError

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        try:
            mod = import_module(self.SETTINGS_MODULE)
        except ImportError as e:
            raise ImportError(
                "Could not import settings '%s' (Is it on sys.path? Is there an import error in the settings file?): %s"
                % (self.SETTINGS_MODULE, e)
            )

        # Settings that should be converted into tuples if they're mistakenly entered
        # as strings.
        tuple_settings = (
            "INSTALLED_APPS", "TEMPLATE_DIRS"
        )

        for setting in dir(mod):
            if setting == setting.upper():
                setting_value = getattr(mod, setting)
                if setting in tuple_settings and \
                        isinstance(setting_value, six.string_types):
                    warnings.warn("The %s setting must be a tuple. Please fix your "
                                  "settings, as auto-correction is now deprecated." % setting,
                                  DeprecationWarning, stacklevel=2)
                    setting_value = (setting_value,) # In case the user forgot the comma.
                setattr(self, setting, setting_value)



settings = Settings()
