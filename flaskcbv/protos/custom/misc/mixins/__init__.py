from jinja2.exceptions import TemplateNotFound
from flask import request, render_template
from flaskcbv.response import Response
from flaskcbv.view import View, TemplateIsAjaxView
from flaskcbv.view.mixins import JSONMixin, getArgumentMixin
from flaskcbv.conf import settings


class DefaultContextVars(object):
    def get_context_data(self, *args, **kwargs):

        context_ = {}
        context_['STATIC_URL'] = settings.STATIC_URL
        try: context_['AUTH_SESSION'] = self.session_id
        except: context_['AUTH_SESSION'] = None
        context_['REQUEST'] = self.request

        context = super(DefaultContextVars, self).get_context_data(*args, **kwargs)
        context_.update(context)
        return context_



class myTemplateView(DefaultContextVars, getArgumentMixin, TemplateIsAjaxView):

    def render_template(self, *args, **kwargs):
        try:
            return super(TemplateIsAjaxView, self).render_template(*args, **kwargs)
        except TemplateNotFound:
            context = self.get_context_data(*args, **kwargs)
            context['ajax_content_tpl'] = self.get_template_name(is_ajax=True)
            return render_template('misc/static.tpl', **context)



class JSONView(getArgumentMixin, JSONMixin, View):

    def get_json_indent(self):
        return self.__json_indent

    def dispatch(self, request, *args, **kwargs):
        try: self.__json_indent = int(request.args['json_indent'])
        except: self.__json_indent = None
        return Response(self.get_as_json())



