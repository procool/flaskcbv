import logging


class Form(object):
    """Base form class for FlaskCBV.

    Supports Django-like ``clean_<field>()`` methods for per-field
    validation.  Use with ``FormViewMixin`` for automatic form handling::

        class MyForm(Form):
            def clean_email(self, value):
                if '@' not in value:
                    raise ValueError('Invalid email')
                return value.lower()

    Attributes:
        raw_data (dict): Unprocessed data as received (e.g. ImmutableMultiDict).
        data (dict): Shallow copy of raw_data as a plain dict.
        cleaned_data (dict): Field values after successful ``clean_*`` calls.
        errors (dict): Field name → error message for failed ``clean_*`` calls.
        view: The view instance that created this form.
    """

    def __init__(self, data={}, view=None, **kwargs):
        self.raw_data = data
        self.view = view
        self.cleaned_data = {}
        self.errors = {}

        ## Create simple dict from raw data(maybe it's ImutableMultiDict)
        self.data = {}
        for key in data:
            self.data[key] = self.raw_data[key]


    def get_clean_def(self, obj, attr):
        def clean_def(value):
            if attr in self.cleaned_data:
                return self.cleaned_data[attr]
            return value
        return clean_def



    def validate(self, *args, **kwargs):
        """Run all clean methods and return whether the form is valid.

        Returns:
            bool: True if no errors were produced, False otherwise.
        """
        self.clean(*args, **kwargs)
        return self.is_clean

    def clean(self, *args, **kwargs):
        """Execute all ``clean_<field>`` methods and populate ``cleaned_data``.

        Fields that raise an exception have their message stored in
        ``self.errors`` and are excluded from ``cleaned_data``.  Fields
        without a corresponding ``clean_`` method are copied as-is.
        """

        clean_defs = []
        if hasattr(self, 'get_clean_defs'):
            clean_defs = self.get_clean_defs()

        for attr in dir(self):
            if not attr.startswith('clean_'):
                continue
            if attr in clean_defs:
                continue
            clean_defs.append(attr)

        for attr in clean_defs:
            item = attr[6:] ## "clean_"
            if not item in self.data:
                self.data[item] = None
            try:
                self.cleaned_data[item] = getattr(self, attr)(self.data[item])
            except Exception as err:
                self.errors[item] = str(err)
                continue

        ## For all key that haven't processing defs: copy them from data to cleaned_data:
        for key in self.data:
            attr = 'clean_%s' % key
            if attr in clean_defs:
                continue
            self.cleaned_data[key] = self.data[key]


    @property
    def is_clean(self):
        """True if no validation errors have been recorded.

        Returns:
            bool: True when ``self.errors`` is empty.
        """
        if not self.errors:
            return True
        return False




