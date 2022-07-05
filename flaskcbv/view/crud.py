import logging
import hashlib, os
from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer

from werkzeug.security import safe_str_cmp

from flask import abort, redirect, url_for
from flaskcbv.response import Response
from .generic import TemplateView

try:
    from flask import current_app
    secret_key = current_app.secret_key
except Exception as err:
    current_app = None
    secret_key = 'veryimportantsecretkey'

dt_s = URLSafeTimedSerializer(secret_key, salt='flaskcbv-csrf-token')

class FormMixin(object):
    form_class = None  # Form class
    form_success_url = None
    form_unsuccess_url = None

    def get_from_success_url(self):
        return self.form_success_url

    def get_from_unsuccess_url(self):
        return self.form_unsuccess_url

    def get_form_class(self):
        return self.form_class

    def get_form_class_kwargs(self, **kwargs):
        data = {}
        data.update(kwargs)
        return kwargs

    def get_form(self, form_class=None, instance=None, **kwargs):
        if instance is None:
            instance = self
        if form_class is None:
            form_class = self.get_form_class()
        form_params = self.get_form_class_kwargs(data=self.request.form, view=instance, **kwargs)
        return form_class(**form_params)

    def get_form_postprocess_url(self, is_valid=False):
        if is_valid and self.get_form_success_url() is not None:
            return self.get_form_success_url()
        elif not is_valid and self.get_form_unsuccess_url() is not None:
            return self.get_form_unsuccess_url()
        else:
            raise ValueError('No URL to redirect to.  Either provide a url by "form_success_url" attr or "get_from_success_url" method.')

    def form_valid(self, form, *args, **kwargs):
        return redirect(self.get_form_postprocess_url(True))

    def form_invalid(self, form, *args, **kwargs):
        return redirect(self.get_form_postprocess_url(False))


    ## Check CSRF Token by session and form values:
    def csrf_check_token(self, form):
        field_name = 'csrf_token'
        time_limit = 3600
        token_s = self.session.pop(field_name, None)
  
        if token_s is None or not field_name in form.data:
            raise Exception('No CSRF token found in session or in data')

        try:
            token = dt_s.loads(form.data[field_name], max_age=time_limit)
        except SignatureExpired:
            raise Exception('The CSRF token has expired')
        except BadData:
            raise Exception('The CSRF token is invalid')

        if not safe_str_cmp(token_s, token):
            raise Exception('Wrong CSRF token')


    ## Generate CSRF Token and store it into session and context(if defined):
    def csrf_gen_token(self, context=None):
        field_name = 'csrf_token'
        if field_name not in self.session:
            self.session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()

        secured_json = dt_s.dumps(self.session[field_name])
        if context is not None:
            context[field_name] = secured_json
        return secured_json




class FormViewMixin(FormMixin):
    csrf_check = True

    def get_context_data(self, *args, **kwargs):
        context = super(FormViewMixin, self).get_context_data(*args, **kwargs)
        if not 'form' in context:
            context['form'] = self.get_form()

        ## Generate CSRF token if enabled:
        if self.csrf_check:
            self.csrf_gen_token(context)

        return context

    def post(self, *args, **kwargs):
        form = self.get_form()

        ## Make CSRF Check if enabled:
        if self.csrf_check:
            try:
                self.csrf_check_token(form)
            except Exception as err:
                form.errors['csrf_token'] = '%s' % err

        if form.validate():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_invalid(self, form, *args, **kwargs):
        kwargs['form'] = form
        data = self.render_template(*args, **kwargs)
        return Response(data)


