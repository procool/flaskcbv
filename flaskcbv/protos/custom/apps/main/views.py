import logging
import datetime

from flask import url_for, session
from misc.mixins import myTemplateView, JSONView

class mainPageView(myTemplateView):
    template='mainpage/mainpage-ajax.tpl'

    def get_context_data(self, **kwargs):
        self.check_for_ip()
        return super(mainPageView, self).get_context_data(**kwargs)


