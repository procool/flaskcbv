import os, sys
import logging

from base import get_flask

from flaskcbv.conf import settings
from flaskcbv.templates import register_tags


class CBVCore(object):
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
        from urls import namespases
        try:
            from urls import namespases
        except Exception as err:
            raise(Exception("%s: You should create urls.py in your project directory!" % err))

        for url in namespases:
            logging.debug('FlaskCBV: Registering url: %s' % url)
            url[0].obj.current_url = url[2]
            url[0].obj.url = url[0] ## backref to view.url
            self.app.add_url_rule(url[1], url[2], url[3], **url[4])


engine = CBVCore()
