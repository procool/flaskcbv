import os, sys
import logging

from jinja2 import FileSystemLoader
from flask import Flask as FlaskBase
from functools import cached_property

from flaskcbv.request import Request

class Flask(FlaskBase):
    """Flask subclass used internally by FlaskCBV.

    Replaces the default request class with FlaskCBV's ``Request`` and
    provides a configurable multi-directory Jinja2 template loader.
    """

    request_class = Request

    def __init__(self, *args, **kwargs):
        try:
            self.__template_folders = kwargs.pop('template_folders')
        except KeyError:
            self.__template_folders = None
        try:
            self.__applications = kwargs.pop('applications')
        except KeyError:
            self.__applications = []
        super(Flask, self).__init__(*args, **kwargs)

    @cached_property
    def jinja_loader(self):
        """The Jinja loader for this package bound object.
        """
        dirs_ = []
        if self.__template_folders is not None:
            for dir_ in self.__template_folders:
                dirs_.append(os.path.join(self.root_path, dir_))

        for app in self.__applications:
            dirs_.append(os.path.abspath(os.path.join(app, 'templates')))

        if len(dirs_) > 0:
            logging.debug('TEMPLATE DIRECTORIES: %s' % dirs_)
            return FileSystemLoader(dirs_)
        logging.warning('FlaskCBV: no template directories configured, template rendering will not work')
        return FileSystemLoader([])

    ## Returns all defined urls:
    def get_all_urls(self, with_defs=False, **kwargs):
        if with_defs:
            return self.view_functions
        return list(self.view_functions.keys())
        



flask_ = [None]


def get_flask(**setts):
    """Return the singleton ``Flask`` instance, creating it if necessary.

    Subsequent calls with no arguments return the already-created instance.
    Pass ``**setts`` only on the first call (done internally by ``CBVCore``).

    Args:
        **setts: Keyword arguments forwarded to the ``Flask`` constructor
            on first call.

    Returns:
        Flask: The application singleton.
    """
    if flask_[0] is None:
        flask_[0] = Flask(__name__, **setts)
    return flask_[0]


