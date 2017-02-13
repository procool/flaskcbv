import logging


class Form(object):
    def __init__(self, data={}, view=None):
        self.raw_data = data
        self.view = view
        self.cleaned_data = {}
        self.errors = {}

        ## Create simple dict from raw data(maybe it's ImutableMultiDict)
        self.data = {}
        for key in data.keys():
            self.data[key] = self.raw_data[key]


    def get_clean_def(self, obj, attr):
        def clean_def(value):
            if attr in self.cleaned_data:
                return self.cleaned_data[attr]
            return value
        return clean_def



    def validate(self, *args, **kwargs):
        return self.clean(*args, **kwargs)

    def clean(self, *args, **kwargs):

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
            if not item in self.data.keys():
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
        if len(self.errors.keys()) == 0:
            return True
        return False




