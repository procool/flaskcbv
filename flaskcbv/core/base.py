import os, sys
import logging

from jinja2 import FileSystemLoader
from flask import Flask as FlaskBase
from flask.helpers import locked_cached_property

from flaskcbv.request import Request

class Flask(FlaskBase):
    request_class = Request

    def __init__(self, *args, **kwargs):
        try: self.__template_folders = kwargs.pop('template_folders')
        except: self.__template_folders = None
        try: self.__applications = kwargs.pop('applications')
        except: self.__applications = []
        super(Flask, self).__init__(*args, **kwargs)

    @locked_cached_property
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

    ## Returns all defined urls:
    def get_all_urls(self, with_defs=False, **kwargs):
        if with_defs:
            return self.view_functions
        return self.view_functions.keys()
        



flask_ = [None]
def get_flask(**setts):
    if flask_[0] is None:
        flask_[0] = Flask(__name__, **setts)
    return flask_[0]


