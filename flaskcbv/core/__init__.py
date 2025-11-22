import os, sys
import logging

from flaskcbv.core.base import get_flask

from flaskcbv.conf import settings
from flaskcbv.templates import register_tags


class CBVCore(object):
    """Central engine that wires together Flask, settings, URLs, and template tags.

    Instantiate via ``create_engine()`` — do not call directly.

    Attributes:
        app (Flask): The underlying Flask application instance.
        views (list): View objects registered after ``make_urls()`` runs.
    """

    def __init__(self, **kwargs):

        setts = {
            #'template_folder': settings.TEMPLATE_PATH[0],
            'template_folders': settings.TEMPLATE_PATH,
            'static_folder': settings.STATIC_PATH,
            'static_url_path': settings.STATIC_URL,
            'applications': settings.APPLICATIONS,
        }
        setts.update(kwargs)


        self.app = get_flask(**setts)
        try: 
            self.app.config.from_object(settings.FLASKCONFIG)
        except Exception as err:
            logging.error("Error on apply flask config: %s" % err)
            pass
        self.make_urls()

        ## Register template tags:
        register_tags(self.app.jinja_env)

    def make_urls(self):
        """Import ``urls.namespases`` and register each route with Flask.

        Raises:
            Exception: If ``urls.py`` cannot be imported from the project path.
        """
        self.views = []
        try:
            from urls import namespases
        except Exception as err:
            raise Exception("%s: You should create urls.py in your project directory!" % err)

        for url in namespases:
            logging.debug('FlaskCBV: Registering url: %s' % url)
            url[0].obj.current_url = url[2]
            url[0].obj.url = url[0] ## backref to view.url
            self.views.append(url[0].obj)
            self.app.add_url_rule(url[1], url[2], url[3], **url[4])


def create_engine(**kwargs):
    """Create and return a ``CBVCore`` engine instance.

    This is the only supported way to initialise the framework.
    Call it in your ``project.py`` **after** ``FLASK_SETTINGS_MODULE``
    is set in the environment::

        from flaskcbv.core import create_engine

        engine = create_engine()
        application = engine.app
        application.secret_key = 'your-secret-key'

    Args:
        **kwargs: Extra settings forwarded to the ``Flask`` constructor,
            overriding values read from the settings module.

    Returns:
        CBVCore: Initialised engine with ``engine.app`` ready to serve.
    """
    ## Factory function: creates and returns a CBVCore engine instance.
    ## Must be called explicitly in project.py after setting FLASK_SETTINGS_MODULE.
    return CBVCore(**kwargs)
