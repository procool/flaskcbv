import logging
import hashlib, hmac, os
from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer

from flask import abort, current_app, redirect, url_for
from flaskcbv.conf import settings
from flaskcbv.response import Response
from flaskcbv.exceptions import ConfigurationError, CSRFError
from .generic import TemplateView


def _get_dt_s():
    """Return a URLSafeTimedSerializer bound to the current app's SECRET_KEY.

    Called lazily inside request context so the key is always read from
    the live Flask config rather than captured at import time.

    Returns:
        URLSafeTimedSerializer: Serializer with salt ``flaskcbv-csrf-token``.

    Raises:
        ConfigurationError: If ``current_app.secret_key`` is falsy.
    """
    ## Получаем сериализатор с ключом из текущего Flask-приложения:
    secret_key = current_app.secret_key
    if not secret_key:
        raise ConfigurationError('SECRET_KEY не задан в конфигурации Flask-приложения')
    return URLSafeTimedSerializer(secret_key, salt='flaskcbv-csrf-token')

class FormMixin(object):
    """Mixin that adds form handling and CSRF protection to a view.

    Attributes:
        form_class: The ``Form`` subclass to instantiate.
        form_success_url (str): Redirect target after a valid submission.
        form_unsuccess_url (str): Redirect target after an invalid submission.
    """

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
        """Instantiate and return the form for the current request.

        Args:
            form_class: Override the class-level ``form_class``.
            instance: View instance to pass as ``view=`` to the form.
                Defaults to ``self``.
            **kwargs: Extra keyword arguments forwarded to the form constructor.

        Returns:
            Form: A form instance populated with ``request.form`` data.
        """
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
        """Validate the CSRF token from the submitted form against the session.

        Pops ``csrf_token`` from the session after reading it so the token
        can only be used once per form submission.

        Args:
            form (Form): The submitted form containing ``csrf_token`` field.

        Raises:
            CSRFError: If the token is missing, expired, or does not match.
        """
        field_name = 'csrf_token'
        time_limit = getattr(settings, 'CSRF_TOKEN_MAX_AGE', 3600)
        token_s = self.session.pop(field_name, None)

        if token_s is None or not field_name in form.data:
            raise CSRFError('No CSRF token found in session or in data')

        try:
            token = _get_dt_s().loads(form.data[field_name], max_age=time_limit)
        except SignatureExpired:
            raise CSRFError('The CSRF token has expired')
        except BadData:
            raise CSRFError('The CSRF token is invalid')

        if not hmac.compare_digest(token_s, token):
            raise CSRFError('Wrong CSRF token')


    ## Generate CSRF Token and store it into session and context(if defined):
    def csrf_gen_token(self, context=None):
        """Generate a signed CSRF token and store it in the session.

        Idempotent within a single session: calling this method twice
        returns the same token.  The raw session value is a SHA-1 hex
        digest; the returned value is a URL-safe signed string.

        Args:
            context (dict, optional): If provided, the signed token is
                also written to ``context['csrf_token']``.

        Returns:
            str: Signed, URL-safe CSRF token ready for embedding in a form.
        """
        field_name = 'csrf_token'
        if field_name not in self.session:
            self.session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()

        secured_json = _get_dt_s().dumps(self.session[field_name])
        if context is not None:
            context[field_name] = secured_json
        return secured_json




class FormViewMixin(FormMixin):
    """TemplateView mixin that wires form handling into GET/POST automatically.

    On GET: adds the form instance and CSRF token to the template context.
    On POST: validates the form and calls ``form_valid()`` or ``form_invalid()``.

    Attributes:
        csrf_check (bool): Enable CSRF validation on POST. Default True.
    """

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


