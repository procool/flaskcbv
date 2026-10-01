# Testing

> Русская версия: [docs/testing_rus.md](testing_rus.md)

---

## Quick start

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

Run the full suite:

```bash
pytest
```

---

## Running specific tests

```bash
pytest -v                                              # verbose: show each test name
pytest -x                                             # stop on first failure
pytest -s                                             # show print/log output
pytest -k "csrf"                                      # keyword filter
pytest tests/test_forms.py                            # single file
pytest tests/test_views.py::TestViewHTTPMethods       # single class
pytest tests/test_csrf.py::TestCsrfCheckToken::test_valid_token_passes  # single test
```

---

## Coverage

```bash
coverage run -m pytest
coverage report                    # summary in terminal
coverage html && open htmlcov/index.html   # HTML report
```

Current total coverage: **84%**.  
CI enforces a minimum of **75%** (`--fail-under=75` in `.github/workflows/test.yml`).

---

## Test infrastructure

The `tests/` directory contains three supporting files that are not test files:

| File | Purpose |
|------|---------|
| `tests/conftest.py` | pytest fixtures shared across all test files |
| `tests/settings.py` | Minimal flaskcbv settings module loaded during tests |
| `tests/urls.py` | Minimal URL config with two views (`/` and `/about`) |

### Fixtures (`conftest.py`)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `engine` | session | Single `CBVCore` instance for the whole test run |
| `app` | session | Flask test app with `TESTING=True` and `SECRET_KEY` set |
| `client` | function | Flask test client — use for HTTP-level tests |
| `app_ctx` | function | Active application context — use when `current_app` is needed |
| `req_ctx` | function | Active request context — use when `flask.request` is needed |

**Rule of thumb:**
- Testing HTTP responses → `client`
- Testing view methods / response objects → `req_ctx`
- Testing URL registration / `get_all_urls()` → `app_ctx`

---

## Test files

### `test_views.py` — Views (142 tests total, 26 here)

| Class | What is tested |
|-------|---------------|
| `TestViewHTTPMethods` | GET/POST return 200, unknown method returns 405, 404 on missing route |
| `TestViewAsView` | `as_view()` returns callable, sets `__name__`, `view_class`, `AVAILABLE_METHODS` |
| `TestViewOptionsIsolation` | Class-level `options` dict is not mutated by instance `__init__`; each instance gets its own copy |
| `TestViewMethodsAlias` | `AVAILABLE_METHODS` ↔ `AVALIBLE_METHODS` sync via `__init_subclass__`; base aliases are the same object |
| `TestTemplateIsAjaxView` | Ajax/non-ajax template name selection; inverted `-ajax` template names; explicit `is_ajax` override |
| `TestViewGetAllUrls` | `get_all_urls()` returns list containing registered endpoint names |
| `TestViewAbortException` | `is_abort_exception` / `test_abort_exception` detect and re-raise HTTP exceptions |

### `test_response.py` — Response (21 tests)

| Class | What is tested |
|-------|---------------|
| `TestResponseString` | Plain string body, empty string, status 200 |
| `TestResponseCallable` | Callable invoked at render time (not at construction); lambda support |
| `TestResponseGenerator` | Generator streamed correctly; both parts present in response body |
| `TestResponseHeaders` | `add_header()` stored; appears in rendered response; `render(headers=)` merged |
| `TestResponseRedirect` | 302 default, custom code (301), `status=` honoured, headers forwarded |
| `TestResponseStatus` | `status=` applied to string and generator bodies; headers kept |
| `TestResponseNotModified` | 304 status, `ETag` header; run as WSGI: empty body, no `Content-Length`; `status` is a class default |

### `test_getargument.py` — getArgumentMixin (9 tests)

| Class | What is tested |
|-------|---------------|
| `TestGetArgumentSmart` | GET/POST/session lookup and GET-over-POST order; `KeyError` without `default` (backward compatibility); `default` returned when missing, `default=None` honoured, found value beats default, disabled source falls to default |

### `test_jsonmixin.py` — JSONMixin (13 tests)

| Class | What is tested |
|-------|---------------|
| `TestJSONMixinEnvelope` | Default `errno/error/details` envelope; context merged; extra kwargs merged; valid JSON output |
| `TestJSONMixinInclude` | `json_response_include()` filters to listed keys; missing keys silently ignored; `None` means all keys |
| `TestJSONMixinExclude` | Default excludes `request`; custom exclude list; missing key in exclude ignored |
| `TestJSONMixinError` | `json_error()` default and custom fields; exception in `get_context_data` returns error envelope |

### `test_forms.py` — Forms (11 tests)

| Class | What is tested |
|-------|---------------|
| `TestFormInit` | Empty data, data copied from raw dict, `ImmutableMultiDict` compatibility |
| `TestFormValidation` | Valid/invalid data, field-level `clean_*` methods, `cleaned_data` population, error accumulation, `is_clean` flag |

### `test_csrf.py` — CSRF protection (10 tests)

| Class | What is tested |
|-------|---------------|
| `TestGetDtS` | Raises without `SECRET_KEY`; returns serializer; uses app's secret key |
| `TestCsrfGenToken` | Token stored in session; returned as string; idempotent within session |
| `TestCsrfCheckToken` | Valid token passes; missing session token raises; missing form field raises; invalid/wrong token raises `CSRFError` |

### `test_request.py` — Request (6 tests)

| Class | What is tested |
|-------|---------------|
| `TestRemoteAddressUntrusted` | `X-Real-IP` ignored when `TRUSTED_PROXIES` is empty; unknown peer not trusted |
| `TestRemoteAddressTrusted` | `X-Real-IP` used when peer is in `TRUSTED_PROXIES`; fallback when header absent; multiple proxies |

### `test_url.py` — URL routing (11 tests)

| Class | What is tested |
|-------|---------------|
| `TestUrlClass` | `Url` stores path/name; `endpoint` with and without namespace; raises without name |
| `TestMakeUrls` | Returns list; 5-element structure per entry; multiple URLs |
| `TestInclude` | `include()` sets namespace on all entries; updates endpoint string |

### `test_conf.py` — Settings (9 tests)

| Class | What is tested |
|-------|---------------|
| `TestDefaultSettings` | All default values present (`TEMPLATE_PATH`, `STATIC_PATH`, `STATIC_URL`, `DEFAULT_HEADERS`) |
| `TestSettings` | Module attribute set; values read from module; defaults applied for missing keys; raises without env var; raises on bad module name |

### `test_cli.py` — CLI commands (18 tests)

| Class | What is tested |
|-------|---------------|
| `TestTokenGen` | `CommonMixin.token_gen()` length, charset, caching |
| `TestGenToken` | `cmdInitProject.gen_token()` length, type, uniqueness |
| `TestGetCliCommands` | `initproject` registered and callable |
| `TestStartApp` | `startapp` registered; creates expected files; app name in `views.py`; raises without name; raises if directory exists |
| `TestInitProject` | `build_proto` creates file from template; raises if file already exists |

---

## Coverage by module

| Module | Coverage | Notes |
|--------|----------|-------|
| `response.py` | 98% | |
| `jsonmixin.py` | 100% | |
| `exceptions.py` | 100% | |
| `forms/form.py` | 86% | |
| `view/generic.py` | 77% | `TemplateView` rendering not covered (needs real templates) |
| `view/crud.py` | 56% | `FormViewMixin` POST flow not covered |
| `scripts/cliargs.py` | 42% | Full CLI argument parsing loop not tested |
| `templates/__init__.py` | 25% | Template tag registration not covered |
| `view/mixins/getargument.py` | 22% | `GetArgumentMixin` not covered |
