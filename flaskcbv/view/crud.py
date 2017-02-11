from flask import abort, redirect, url_for
from generic import TemplateView

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

    def get_form(self, form_class=None, instance=None):
        if instance is None:
            instance = self
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.form, instance)

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



class FormViewMixin(FormMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(FormViewMixin, self).get_context_data(*args, **kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.validate():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form, *args, **kwargs):
        kwargs['form'] = form
        return self.render_template(*args, **kwargs)

