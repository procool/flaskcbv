# FlaskCBV API Reference

> Русская версия: [docs/api_rus.md](api_rus.md)

---

## Requirements

| Component | Version |
|-----------|---------|
| Python    | >= 3.8  |
| Flask     | >= 2.0  |
| Werkzeug  | >= 2.1  |

---

## flaskcbv.core — Engine initialisation

### `create_engine(**kwargs)`

Factory function that creates and returns a `CBVCore` instance.
Must be called explicitly in `project.py` after `FLASK_SETTINGS_MODULE` is set.

```python
from flaskcbv.core import create_engine

engine = create_engine()
application = engine.app
application.secret_key = 'your-secret-key'
```

**Args:** `**kwargs` — override any setting passed to the `Flask` constructor.  
**Returns:** `CBVCore` instance with `.app` ready to serve requests.

---

### `class CBVCore`

Central engine. Reads settings, creates the Flask app singleton, registers
URL rules from `urls.namespases`, and loads template tags.

| Attribute | Description |
|-----------|-------------|
| `app` | The underlying `Flask` instance. |
| `views` | List of view objects registered after `make_urls()`. |

---

## flaskcbv.url — URL routing

### `class Url(url, obj, name=None, namespace=None)`

Binds a URL path to a view.

```python
Url('/users/<int:id>', UserView(), name='user_detail')
```

| Arg | Description |
|-----|-------------|
| `url` | URL path string, e.g. `'/users/<int:id>'`. |
| `obj` | A `View` instance, `as_view()` callable, or `include()` result. |
| `name` | Endpoint name for `url_for()`. Required unless `obj` is an `include()`. |
| `namespace` | Set automatically by `include()`. |

**Property `endpoint`** — returns `'namespace:name'` or `'name'`.  
Raises `Exception` if `name` was not provided.

---

### `make_urls(*namespases)`

Build the URL table for `CBVCore`. Call this in your project's `urls.py`
and assign the result to `namespases`.

```python
from flaskcbv.url import Url, make_urls

namespases = make_urls(
    Url('/',      IndexView(), name='index'),
    Url('/about', AboutView(), name='about'),
)
```

---

### `include(namespases, namespace=None, description=None)`

Mount a sub-application's URL list under a namespace.

```python
from apps.blog import urls as blog_urls

namespases = make_urls(
    Url('/blog', include(blog_urls.namespases, namespace='blog')),
)
```

---

## flaskcbv.view — Views

### `class View`

Base class-based view. Define HTTP-method handlers as instance methods:

```python
from flaskcbv.view import View
from flaskcbv.response import Response

class MyView(View):
    def get(self, request, *args, **kwargs):
        return Response('Hello')

    def post(self, request, *args, **kwargs):
        return Response('Posted')
```

**Key attributes / methods:**

| Name | Description |
|------|-------------|
| `AVAILABLE_METHODS` | List of allowed HTTP methods. Others return 405. Default: `["GET", "POST", "OPTIONS", "HEAD"]`. |
| `AVALIBLE_METHODS` | **Deprecated.** Alias for `AVAILABLE_METHODS`, kept in sync automatically. Will be removed in a future major version. |
| `options` | Extra kwargs forwarded to `add_url_rule()`. |
| `decorators` | View-level decorators applied by `as_view()`. |
| `request` | Current Flask request object. |
| `session` | Current Flask session object. |
| `prepare(*args, **kwargs)` | Entry point called by Flask per request. |
| `dispatch(request, *args, **kwargs)` | Routes to the correct method handler. |
| `get_headers(**kwargs)` | Override to add custom response headers. |
| `get_current_url()` | Returns the URL path of this view. |
| `get_all_urls(**kwargs)` | Returns all registered endpoint names. |
| `is_abort_exception(ex)` | True if `ex` is a werkzeug HTTP exception. |
| `test_abort_exception(ex)` | Re-raises `ex` if it is an HTTP exception. |

---

### `class TemplateView`

Extends `View` with Jinja2 template rendering.

```python
from flaskcbv.view import TemplateView

class HomeView(TemplateView):
    template = 'home/index.tpl'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Home'
        return ctx
```

**Key methods:**

| Name | Description |
|------|-------------|
| `template` | Path to the Jinja2 template. |
| `get_template_name()` | Returns the template path; override to compute it dynamically. |
| `get_context_data(**kwargs)` | Returns the template context dict. Adds `request` automatically. |
| `render_template(*args, **kwargs)` | Renders the template and returns an HTML string. |

---

### `class TemplateIsAjaxView`

Extends `TemplateView`. Serves `index-ajax.tpl` for AJAX requests
and `index.tpl` for regular ones (or vice versa).

---

## flaskcbv.view.crud — Form handling

### `class FormMixin`

Adds form instantiation and CSRF protection to a view.

| Attribute | Description |
|-----------|-------------|
| `form_class` | The `Form` subclass to use. |
| `form_success_url` | Redirect URL after a valid submission. |
| `form_unsuccess_url` | Redirect URL after an invalid submission. |

**Key methods:**

| Name | Description |
|------|-------------|
| `get_form(form_class, instance, **kwargs)` | Instantiates and returns the form. |
| `form_valid(form)` | Called when form validates. Default: redirect to `form_success_url`. |
| `form_invalid(form)` | Called on failure. Default: redirect to `form_unsuccess_url`. |
| `csrf_gen_token(context)` | Generates a signed CSRF token and stores it in the session. |
| `csrf_check_token(form)` | Validates the CSRF token. Raises `CSRFError` on failure. |

---

### `class FormViewMixin(FormMixin)`

Combines `FormMixin` with `TemplateView` automation.

- **GET** — injects `form` and `csrf_token` into the template context.
- **POST** — validates the form; calls `form_valid()` or `form_invalid()`.

```python
from flaskcbv.view.crud import FormViewMixin
from flaskcbv.view import TemplateView

class ContactView(FormViewMixin, TemplateView):
    template = 'contact.tpl'
    form_class = ContactForm
    form_success_url = '/thank-you/'
```

| Attribute | Description |
|-----------|-------------|
| `csrf_check` | Enable CSRF validation on POST. Default `True`. |

---

## flaskcbv.view.mixins — Mixins

### `class getArgumentMixin`

Provides `get_argument_smart()` for unified parameter lookup across GET,
POST, cookie, and session sources.

```python
value = self.get_argument_smart('user_id', as_get=True, as_post=True)
```

Raises `KeyError` if the key is absent from all enabled sources.

Sources are checked in order: GET → POST → cookie → session.

---

### `class JSONMixin`

Serialises `get_context_data()` output to a JSON response body.

```python
class MyAPI(JSONMixin, View):
    def dispatch(self, request, *args, **kwargs):
        return Response(self.get_as_json())
```

| Method | Description |
|--------|-------------|
| `get_as_json(**data)` | Returns JSON string from context + `data`. |
| `json_error(errno, error, details)` | Returns a JSON error response. |
| `json_response_include()` | Return a list of context keys to include (default: all). |
| `json_response_exclude()` | Return a list of context keys to exclude. Default: `['request']`. |
| `get_json_indent()` | Override to pretty-print JSON. Default: `None`. |

Default response structure:

```json
{
    "errno": 0,
    "error": "Ok",
    "details": "",
    "...": "view context keys"
}
```

On `get_context_data()` failure:

```json
{
    "errno": -1,
    "error": "Failed",
    "details": "error message"
}
```

---

## flaskcbv.forms — Forms

### `class Form`

Base form with Django-like `clean_<field>()` validation.

```python
from flaskcbv.forms import Form

class LoginForm(Form):
    def clean_username(self, value):
        if not value:
            raise ValueError('Username is required')
        return value.strip()
```

| Attribute | Description |
|-----------|-------------|
| `raw_data` | Original data dict (may be ImmutableMultiDict). |
| `data` | Shallow copy as a plain `dict`. |
| `cleaned_data` | Validated values after `clean()`. |
| `errors` | Field name → error message for failed fields. |

| Method | Description |
|--------|-------------|
| `validate()` | Run `clean()` and return `is_clean`. |
| `clean()` | Execute all `clean_<field>()` methods. |
| `is_clean` | `True` when `errors` is empty. |

---

## flaskcbv.request — Request

### `class Request`

Extended Flask request. Used automatically by all views.

| Property | Description |
|----------|-------------|
| `remote_address` | Client IP from `HTTP_X_REAL_IP` or `REMOTE_ADDR`. |
| `is_ajax` | `True` if `X-Requested-With: XMLHttpRequest` is present. |

---

## flaskcbv.response — Response

### `class Response`

Accepts three types of body:

**Plain string** — most common case:
```python
return Response('Hello, world!')
return Response(json.dumps(data))
```

**Callable (function or lambda)** — invoked once at render time.
Useful to defer expensive computation until after the view returns:
```python
def get(self, request, *args, **kwargs):
    return Response(lambda: build_report())
```

> **Note:** pass the callable itself, not its result.
> `Response(fn)` — correct; `Response(fn())` — passes the return value directly.

**Generator** — streamed via `flask.stream_with_context`.
Pass the **generator object** (i.e. call the generator function first):
```python
def generate(n):
    for i in range(n):
        yield 'chunk-%d\n' % i

return Response(generate(100))   # correct: generator object
# return Response(generate)      # wrong: passes the function, not the generator
```

| Method | Description |
|--------|-------------|
| `add_header(name, value)` | Add a custom response header. |
| `render(headers={})` | Build and return `flask.Response`. |

---

### `class ResponseRedirect`

```python
from flaskcbv.response import ResponseRedirect

return ResponseRedirect('/login/', code=302)
```

---

## flaskcbv.exceptions — Exceptions

| Class | Description |
|-------|-------------|
| `FlaskCBVError` | Base exception for all FlaskCBV errors. |
| `ConfigurationError` | Application misconfiguration (e.g. missing `SECRET_KEY`). |
| `CSRFError` | CSRF token missing, expired, or invalid. |

---

## flaskcbv.conf — Settings

Settings are loaded from the module named by the `FLASK_SETTINGS_MODULE`
environment variable.  Unset values fall back to `DefaultSettings`.

```python
from flaskcbv.conf import settings

print(settings.STATIC_URL)   # '/static'
```

**Default values** (`flaskcbv.conf.defaults.DefaultSettings`):

| Setting | Default |
|---------|---------|
| `TEMPLATE_PATH` | `'templates'` |
| `STATIC_PATH` | `'static'` |
| `STATIC_URL` | `'/static'` |
| `DEFAULT_HEADERS` | `{}` |

**Required in your settings module:**

| Setting | Description |
|---------|-------------|
| `APPLICATIONS` | Tuple of application directory paths for template discovery. |
| `FLASKCONFIG` | Module name containing Flask config variables (optional). |

---

## How the framework works

### Startup

1. Reads the settings module name from the `FLASK_SETTINGS_MODULE` environment variable.
2. Creates the `settings` singleton via `flaskcbv.conf.Settings` — all attribute names
   are uppercased.
3. Instantiates `flaskcbv.core.base.Flask` (a subclass of `flask.Flask`), configures
   template search paths, and initialises `jinja_loader`.
4. Processes `urls.py`: calls `add_url_rule` for every registered URL.
5. Discovers and registers template tags via `flaskcbv.templates.register_tags`.

### Request handling

1. Flask calls `prepare()` on the matched view class.
2. `prepare()` calls `dispatch()`, which inspects the HTTP method and delegates
   to the corresponding handler (`get`, `post`, …).
3. The handler returns a `flaskcbv.Response` instance.
4. `prepare()` calls `render()` on the response and returns the result to Flask.

---

## Running tests

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the full test suite from the project root:

```bash
pytest
```

Useful options:

```bash
pytest -v                                   # verbose output
pytest -x                                   # stop on first failure
pytest tests/test_forms.py                  # single file
pytest tests/test_views.py::TestViewHTTPMethods   # single class
pytest -k "csrf"                            # keyword filter
```

Coverage report:

```bash
coverage run -m pytest
coverage report
coverage html && open htmlcov/index.html
```

See the [Russian docs](readme_rus.md) or the "Running Tests" section in
[README.md](../README.md) for a full description of the test infrastructure.

---

## Migrating from 1.x to 2.x

In v2.0.0 the engine is no longer created automatically on import.

**Files to update in every existing project:**

| File | Action |
|------|--------|
| `apps/project.py` | **Required.** Replace the `engine` import with a `create_engine()` call (see below). |
| `apps/flaskconfig.py` | **Required** if `FormViewMixin` is used. Make sure `SECRET_KEY` is set. |
| `apps/start.py` | Recommended. Remove hard-coded `debug=True, host='0.0.0.0'`; read from env vars instead. |
| `setup.py` / `requirements.txt` | Remove `Werkzeug==2.0.0` pin; use `Werkzeug>=2.1`. |

Update `project.py` in every existing project:

```python
## Before (flaskcbv 1.x):
from flaskcbv.core import engine
application = engine.app

## After (flaskcbv 2.x):
from flaskcbv.core import create_engine
engine = create_engine()
application = engine.app
```

Recommended update to `start.py` — replace hard-coded run parameters:

```python
## Before:
application.run(debug=True, host='0.0.0.0', port=5555)

## After:
import os
debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
host  = os.environ.get('FLASK_HOST', '127.0.0.1')
port  = int(os.environ.get('FLASK_PORT', '5000'))
application.run(debug=debug, host=host, port=port)
```

Environment variables for runtime control:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `'false'` | Enable debug mode (`'true'` / `'false'`). |
| `FLASK_HOST` | `'127.0.0.1'` | Bind address. |
| `FLASK_PORT` | `'5000'` | Port number. |
