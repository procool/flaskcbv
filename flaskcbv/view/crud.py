from generic import TemplateView

class FormMixin(object):
    form_class = None  # Form class
    success_url = None

    def get_form_class(self):
        return self.form_class

    def get_form(self, form_class=None, instance=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(request.form, instance)

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ValueError('No URL to redirect to.  Either provide a url or define a get_absolute_url method on the Model.')  # FIXME: Je vhodne vyvolat ValueError?

        return url

    def form_valid(self, form, *args, **kwargs):
        return redirect(self.get_success_url())

    def form_invalid(self, form, *args, **kwargs):
        kwargs['form'] = form
        return self.render_template(*args, **kwargs)



class FormView(FormMixin, TemplateView):

    def get_context_data(self, *args, **kwargs):
        context = super(FormView, self).get_context_data(*args, **kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.validate():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


