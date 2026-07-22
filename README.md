# FlaskCBV

![Tests](https://github.com/procool/flaskcbv/actions/workflows/test.yml/badge.svg)
![Python versions](https://img.shields.io/pypi/pyversions/flaskcbv)
![PyPI version](https://img.shields.io/pypi/v/flaskcbv)
![License](https://img.shields.io/pypi/l/flaskcbv)

## Compatibility

| FlaskCBV | Python      | Flask     | Werkzeug  |
|----------|-------------|-----------|-----------|
| 2.x      | 3.8 – 3.12  | 2.0 – 3.x | ≥ 2.1     |
| 1.x      | 3.6 – 3.8   | 1.x       | 2.0.0     |

> **Python 3.8** is EOL upstream and kept only for legacy instances that cannot
> be upgraded. It is covered by CI, but scheduled for removal in a future
> release once those instances migrate; new code should target 3.9+.

Upgrading from 1.x? See the [migration guide](docs/api.md#migrating-from-1x-to-2x).  
Four files need updating: `apps/project.py` (required), `apps/flaskconfig.py` (required if using forms),
`apps/start.py` (recommended), `Werkzeug` version pin (required).

## Introduction

FlaskCBV is Alternative Framework for working with flask with the class Based Views approach (CBV)

The platform allows to implement a clear architecture based on the using of all the benefits of this approach;

These framework are made in a style similar to Django:
* to simplify its study
* because the architecture of the Django looks elegant.

We tried to make the minimum loaded wrapper for the flask, which does not require any special dependencies.
 
## Features of use:
Instead of the route decorator to define handlers we are using urls.py with the description of the scheme and with ability: 
* using includes
* the splitting of the namespace for each application


As a configuration file for flaskcbv used the "settings" module;
There's also a separate settings module is specifically flask;

## Dependences:
*  setuptools
*  Flask
*  Werkzeug
*  Jinja2
*  MarkupSafe



## Installation and setup:
1. Install framework using pip:

	```
	sudo pip3 install flaskcbv
	```

  The required dependencies will be installed automatically.

2. Create a directory of your project:

	```
	mkdir project; cd project
 	```

4. Create project using flaskcbv utility:

	```
	flaskcbv initproject
 	```

  	The project will be created in the current directory

6. Create assets(static) files directory:

	```
 	mkdir apps/assets;
 	touch apps/assets/some_test.js
 	```
   
	- You can request this file as http://127.0.0.1:5555/static/some_test.js ;
	- You can change the static file location in settings/local.py by variables: STATIC_PATH and STATIC_URL

7. Start server:

   	```
	cd apps;
	python3 start.py
	```

  	The server starts by default on port 5555

8. Try the server using your browser or telnet(in a separate shell), for e.g:

	```
	$ telnet localhost 5555
	Trying 127.0.0.1...
	Connected to localhost.
	Escape character is '^]'.
	GET / HTTP/1.0
	
	HTTP/1.0 200 OK
	Content-Type: text/html; charset=utf-8
	Content-Length: 22
	server: my WEB Server
	Date: Fri, 10 Jun 2016 21:57:46 GMT
	
	It works on FlaskCBV! Connection closed by foreign host.
	
	Project is works, have fun:)
	```





## THE DIRECTORY STRUCTURE

In the generated project by default there are two directories:
*  apps/ - there are placed the applications of project and modules required to run
*  settings/ - flaskcbv settings module

Let us consider separately each of the directories:

### Directory: settings/
*  __init__.py - this module contains the base settings of the framework
*  local.py    - this module is included to the __init__.py, it is necessary for that would allocate the settings concerning the used development instance.

#### For example:
In __init__ you can set up base settings such as the application set, the default headers and so on;
In local.py you can set/override the database connection settings, the paths to templates, etc...
Then if you move project to other instance you can change local.py using a Makefile or other method of automatic creating from prototypes;
it is convenient to push "__init__" into the repository.

If desired, the entire directory of settings can be replaced by settings.py, this is not affect to the framework working;

### Directory: apps/
*  start.py - it is a runnable program, it is necessary to start the server in test mode.
             in this program, are automatically assigned port, and absolute path to the project;
             based on this program you can easily create the front-end wsgi.py
*  project.py - module which creates a flask app using flaskcbv;
*  flaskconfig.py - a module which sets configuration variables of the Flask;

*  urls.py - module which describes the main namespaces and handlers(urls) of the project

Here placed the default app: "main", which makes output on request:
  "It works on FlaskCBV!"
*  main/urls.py - included to the main urls.py module
*  main/views.py - the module contains a view mainView, here also sets the template which is used to output to the user.
*  main/templates/main/index.tpl - template of "main" application;

For the successful work of application "main" it placed to the settings module in the APPLICATIONS tuple;

Try to play with project, to withdraw its templates and to write any mixins.


Now you can use Flask with CBV approach

Have fun!:)

regards, procool@







---

## Running Tests

> Full test documentation — what each test file covers, fixture reference, and coverage breakdown — is in **[docs/testing.md](docs/testing.md)**.

### Prerequisites

Install the framework with development dependencies:

```bash
pip install -e ".[dev]"
```

This installs `pytest`, `pytest-flask`, and `coverage` in addition to the
regular dependencies.

---

### Running the full test suite

From the **project root** (the directory containing `setup.py`):

```bash
pytest
```

pytest will discover all tests automatically using the configuration in
`setup.cfg` (`testpaths = tests`).

---

### Useful pytest options

```bash
## Run with verbose output (show each test name):
pytest -v

## Stop on first failure:
pytest -x

## Run a single test file:
pytest tests/test_forms.py

## Run a single test class:
pytest tests/test_views.py::TestViewHTTPMethods

## Run a single test by name:
pytest tests/test_csrf.py::TestCsrfCheckToken::test_valid_token_passes

## Show stdout output (print statements):
pytest -s

## Run only tests matching a keyword:
pytest -k "csrf"
```

---

### Coverage report

```bash
## Run tests and print a coverage summary:
coverage run -m pytest
coverage report

## Generate an HTML report (opens in browser):
coverage html
open htmlcov/index.html
```

---

### How the test infrastructure works

The test suite lives in the `tests/` directory and contains three
supporting files that are **not test files themselves**:

| File | Purpose |
|------|---------|
| `tests/conftest.py` | pytest fixtures (engine, app, client, contexts) |
| `tests/settings.py` | Minimal flaskcbv settings module for tests |
| `tests/urls.py` | Minimal URL config with two test views |

**Important:** `conftest.py` inserts `tests/` at the front of `sys.path`
and sets `FLASK_SETTINGS_MODULE=settings` **before** importing anything
from flaskcbv. This is required because `flaskcbv.conf` reads the settings
module at import time.

The main fixtures provided by `conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `engine` | session | Single `CBVCore` instance shared across all tests |
| `app` | session | Flask app with `TESTING=True` and `SECRET_KEY` set |
| `client` | function | Flask test client (fresh per test) |
| `app_ctx` | function | Active application context |
| `req_ctx` | function | Active request context |

The `engine` and `app` fixtures are **session-scoped** to avoid duplicate
endpoint registration errors that would occur if the Flask app were
re-created for every test.

---

### What is tested

| File | Covers |
|------|--------|
| `test_forms.py` | `Form` init, data copy, `clean_*` methods, errors, `is_clean`, `ImmutableMultiDict` |
| `test_views.py` | HTTP methods, 404/405, `as_view()`, `get_all_urls()`, abort helpers |
| `test_url.py` | `Url`, `make_urls()`, `include()`, namespaces, endpoints |
| `test_conf.py` | `DefaultSettings`, `Settings` init, missing/invalid `FLASK_SETTINGS_MODULE` |
| `test_csrf.py` | `_get_dt_s()`, `csrf_gen_token()`, `csrf_check_token()`, `ConfigurationError`, `CSRFError` |
| `test_request.py` | `remote_address` with and without `HTTP_X_REAL_IP` header |
| `test_cli.py` | `token_gen()`, `gen_token()`, token uniqueness, CLI commands, `build_proto()` |

---

### Writing new tests

1. Add a `test_*.py` file to `tests/`.
2. Use fixtures from `conftest.py` as function arguments:

```python
def test_my_view(client):
    r = client.get('/')
    assert r.status_code == 200
```

3. For tests that need an app or request context but not HTTP calls,
   use `app_ctx` or `req_ctx`:

```python
def test_something_in_context(app_ctx):
    from flask import current_app
    assert current_app.config['TESTING'] is True
```

4. If you need a new test route, add it to `tests/urls.py`.

5. If you need different settings, monkeypatch `os.environ` and
   instantiate `Settings()` directly — do not modify `tests/settings.py`
   as it is shared across all tests.

---

## FlaskCBV Examples:


### Simple implementation of json server:

	from flaskcbv.response import Response
	from flaskcbv.view.mixins import JSONMixin
	from flaskcbv.view import View
	
	
	
	class JSONView(JSONMixin, View):
	    def get_json_indent(self):
	        return self.__json_indent
	
	    def dispatch(self, request, *args, **kwargs):
	        try: self.__json_indent = int(request.args['json_indent'])
	        except: self.__json_indent = None
	
	        r = super(JSONView, self).dispatch(request, *args, **kwargs)
	
	        ## Return context as json 
	        return Response(self.get_as_json())
	
	
	
	class myJsonView(JSONView):
	    def get_context_data(self, **kwargs):
	        return {'some': 'var'}
	
	
	"""
	when processing myJsonView the client will receive:
	{
	    "errno": 0,
	    "error": "OK",
	    "details": "",
	    "some": "var"
	}
	"""
	
	







### Example of checking user session (implementation LoginRequiredMixin):


	import logging
	
	import werkzeug.exceptions as ex
	from flask import request, session, abort
	
	from flaskcbv.view.mixins import JSONMixin, getArgumentMixin
	from flaskcbv.response import Response
	
	from .models import Auth
	
	
	## Mixin with session validate methods:
	class AuthedMixin(object):
	
	    def test_for_user(self):
	        ## Try to get session from query parameters:
	        try: session_= self.request.args['session']
	        except: session_ = None
	        
	        ## Try to get session from flask.session (cookies)
	        if session_ is None:
	            try: session_=session['session']
	            except: session_= None
	
	        ## No session, return 401:
	        if session_ is None:
	            abort(401)
	
	        ## Check the session, find the user:
	        try:
	            request.user = Auth.session(session_)
	            session['session'] = session_
	        except Exception as err:
	            request.user = None
	
	
	
	## Check session Mixin
	class _LoginRequiredMixin(object):
	    def prepare(self, *args, **kwargs):
	        ## The only type of exception - abort
	        self.test_for_user()
	        
	        ## The session was found but it's wrong(or user not found):
	        if request.user is None:
	            abort(403)
	
	        return super(_LoginRequiredMixin, self).prepare(*args, **kwargs)
	
	
	
	class LoginRequiredMixin(_LoginRequiredMixin, AuthedMixin):
	    pass

    
Now, mixing in LoginRequiredMixin to any view, before the dispatch we have carried out the test of session








### An example of a forwarding context variables to the template:


	import logging
	import datetime
	
	from flaskcbv.view import TemplateView
	from settings import STATIC_URL
	
	## Provide context varialbes from project settings
	class defaultSettingsMixin(object):
	
	    def get_context_data(self, **kwargs):
	        context = super(defaultSettingsMixin, self).get_context_data(**kwargs)
	        context['STATIC_URL'] = STATIC_URL
	        return context
	
	
	
	class myTemplateView(defaultSettingsMixin, TemplateView):
	    pass
	
	
	Now, inheriting myTemplateView in context variables STATIC_URL is set from the settings;
	



### Example of creating and using the template tag(jinja extention):

The classes of template tags should be placed into the directory templatetags located in the root directory of the project;*

Create a directory:

	$ cd myproject
	$ ls
	apps  assets  settings  templates
	$ mkdir templatetags; cd templatetags
	$ touch __init__.py

Let us create, for example, mytags.py in which:

	# encoding: utf8
	from jinja2 import nodes
	from jinja2.ext import Extension
	
	## This extension will return the type of the given attribute any of the specified object
	class ObjectAttrTypeExtension(Extension):
	    ## If this attribute is not defined or is False or None, the extension will not be taken into account when running:
	    enabled=True
	    
	    tags = set(['attrtype'])
	
	    def __init__(self, environment):
	        super(ListSortedExtension, self).__init__(environment)
	
	        # add the defaults to the environment
	        environment.extend(
	            fragment_cache_prefix='',
	            fragment_cache=None
	        )
	
	    def parse(self, parser):
	        lineno = next(parser.stream).lineno
	
	        # now we parse a single expression that is used as cache key.
	        args = [parser.parse_expression()]
	
	        if parser.stream.skip_if('comma'):
	            args.append(parser.parse_expression())
	        else:
	            args.append(nodes.Const(None))
	
	        return nodes.CallBlock(self.call_method('_empty', args),
	                               [], [], "").set_lineno(lineno)
	
	    def _empty(self, obj, attr, caller):
	        try:
	            return "%s" % type(getattr(obj, attr))
	        except Exception as err:
	            pass
	        return u''
	
        
At the start flaskcbv will automatically load the tag and it will be available for using in templates;
There is an Example:

	{% attrtype request, 'method' %}

 - returns: "<type 'str'>"

Read more about jinja2 extentions:
http://jinja.pocoo.org/docs/dev/extensions/






### Example of FlaskCBV Forms:


	## Simple form:
	from flaskcbv.forms import Form
	
	class myFormClass(Form):
	    def clean_test_passed(self, val):
	        ## self.cleaned_data['test_passed'] value will be 'passed' 
	        ## self.data['test_passed'] value will be val
	        return 'passed'      
	
	    def clean_test_error(self, val):
	        ## self.data['test_error'] value will be val
	        ## there is no key 'test_error' in self.cleaned_data
	        ## self.errors['test_error'] will be: 'Some Error' Exception
	        raise Exception('Some Error')
	
	
	
	
	from flaskcbv.view.crud import FormViewMixin
	from flaskcbv.view import TemplateView
	
	
	class myFormView(FormViewMixin, TemplateView):
	    template='index/some.tpl'
	    form_class = myFormClass
	
	    ## Uncomment this, if you want default redirect:
	    #form_success_url = '/action/success/'
	    #form_unsuccess_url = '/action/unsuccess/'
	
	    ## Custom url for form success action:
	    #def get_from_success_url(self):
	    #    return "/some/other/success/url"
	
	    ## Here, on GET client recv's our template, where in context var.: 'form' we can access to cleaned form variables;
	    
	    ## Let's Redefine POST processing:
	    def post(self, *args, **kwargs):
	
	        ## Create our form object:
	        form = self.get_form() 
	
	        ## Check form, this will run form.clean that will start 'clean_ATTR' methods, like in django
	        if form.validate():
	            ## By default it's a redirect to self.form_success_url or self.get_from_success_url(): 
	            return self.form_valid(form)
	
	        else:
	            ## By default returns template with 'form' context variable:
	            return self.form_invalid(form)
	
	
