# Changelog

## [2.3.2] — 2026-09-29

Обратно совместимо: существующий код работает без изменений.

### Добавлено

- **`Response(data, status=None)`** (`flaskcbv/response.py`) — код ответа
  задаётся напрямую. Раньше `Response` всегда отдавал то, что выбрал Flask
  (200), и ответить, например, 304 или 201 без обходных путей было нельзя.
  `None` — прежнее поведение.
- **`ResponseNotModified(etag=None)`** — готовый ответ `304 Not Modified` для
  условных запросов (`If-None-Match`); тело всегда пустое, `etag` повторяется
  в заголовке `ETag`.
- **`get_argument_smart(..., default=...)`**
  (`flaskcbv/view/mixins/getargument.py`) — значение, которое возвращается,
  если ключ не найден ни в одном включённом источнике. Параметр добавлен
  последним; без него, как и прежде, бросается `KeyError`, поэтому вызовы с
  `try/except KeyError` не меняют поведения. `default=None` — допустимое
  значение (отличается от «не передан» внутренним маркером).
- **`ResponseRedirect(url, status=...)`** — `status` учитывается и важнее
  `code`; раньше такой аргумент молча игнорировался бы.
- `Response.status = None` — атрибут класса: наследник, переопределивший
  `__init__` без `super()`, продолжает рендериться.

### Тесты

- `tests/test_response.py`: `TestResponseStatus`, `TestResponseNotModified`,
  `status=` у редиректа (8 новых); `tests/test_getargument.py` — новый файл,
  9 тестов, в том числе на сохранение `KeyError` без `default`. Всего 142.
  Тело 304 проверяется прямым WSGI-вызовом, а не регистрацией маршрута: та
  зависела бы от того, обслужило ли общее приложение уже хоть один запрос.

## [2.3.1] — 2026-07-22

Консолидация двух разошедшихся линий разработки в одну. Объединяет
переименование `namespaces` (линия 2.3.0) с накопленными фичами и тестами
линии разработки (ранее помечалась как 2.2.0). Изменения вносились по диффам
с прогоном тестов на каждом шаге, а не слиянием коммитов.

### Совместимость / Breaking change (обратно совместимо)

- **`flaskcbv/url/__init__.py`** — параметр `*namespases` в `make_urls()`
  переименован в `*namespaces`; параметр `namespases` в `include()` — в
  `namespaces`. Докстринги и примеры обновлены.
- **`flaskcbv/core/__init__.py`** — `CBVCore.make_urls()` принимает как новое
  имя переменной `namespaces` в `urls.py`, так и старое `namespases`
  (с `DeprecationWarning`). Порядок поиска: `namespaces`, затем `namespases`;
  если нет ни одного — `Exception`.
- **`flaskcbv/view/generic.py`**, **`flaskcbv/protos/*/urls.py`**,
  **`flaskcbv/scripts/commands/startapp.py`**, **`tests/*`**,
  **`docs/api.md`**, **`docs/api_rus.md`** — все вхождения `namespases`
  переименованы в `namespaces` (генератор `startapp` теперь создаёт скелет с
  новым именем).

  **Миграция:** переименовать `namespases = make_urls(...)` в
  `namespaces = make_urls(...)` в `urls.py` каждого проекта. До переименования
  фреймворк продолжает работать с `DeprecationWarning`.

### Добавлено (из линии разработки)

- **`TRUSTED_PROXIES`** — `X-Real-IP` доверяется только от перечисленных прокси.
- **`CSRF_TOKEN_MAX_AGE`** — настраиваемый TTL CSRF-токена (`view/crud.py`).
- **`startapp`** — CLI-команда генерации скелета приложения (views/urls/шаблон).
- **`docs/testing.md`** — полный справочник по тест-инфраструктуре.

### Исправлено

- **`Response`** — исправлен баг с `callable`-данными в `_render()` (возвращается
  результат вызова, а не сам объект-функция); `render(headers=None)` и
  `Form(data=None)` вместо изменяемых значений по умолчанию.

### Тесты

- Полный набор: **125 тестов** (добавлены `test_core_make_urls.py` —
  проверка dual-support `namespaces`/`namespases`, а также `test_jsonmixin`,
  `test_response` и др. из линии разработки).

### Версия

- Версия повышена до `2.3.1`.

---

## [2.2.0] — 2026-04-03

### Документация

- **Google-style docstrings** — добавлены docstring'и ко всем публичным классам и методам:
  `flaskcbv/exceptions.py`, `flaskcbv/view/generic.py`, `flaskcbv/view/crud.py`,
  `flaskcbv/forms/form.py`, `flaskcbv/url/__init__.py`, `flaskcbv/core/__init__.py`,
  `flaskcbv/core/base.py`, `flaskcbv/request.py`, `flaskcbv/response.py`,
  `flaskcbv/view/mixins/getargument.py`, `flaskcbv/view/mixins/jsonmixin.py`.
  Выбранный формат: **Google-style** (секции `Args:`, `Returns:`, `Raises:`, `Attributes:`).

- **`docs/api.md`** — создан полный англоязычный API-справочник по всем публичным
  классам и методам фреймворка: `flaskcbv.core`, `flaskcbv.url`, `flaskcbv.view`,
  `flaskcbv.view.crud`, `flaskcbv.view.mixins`, `flaskcbv.forms`, `flaskcbv.request`,
  `flaskcbv.response`, `flaskcbv.exceptions`, `flaskcbv.conf`.

- **`README.md`** — добавлены badges (CI, PyPI version, Python versions, License),
  таблица совместимости (FlaskCBV × Python × Flask × Werkzeug),
  раздел «Running Tests» с описанием инфраструктуры, полезных опций pytest
  и генерации coverage-отчётов.

### Версия

- Версия повышена с `2.1.0` до `2.2.0`.

---

## [2.1.0] — 2026-04-04

### Тесты и CI

- Добавлена тестовая инфраструктура: `tests/conftest.py`, `tests/settings.py`,
  `tests/urls.py` с тестовыми представлениями.
- `tests/test_forms.py` — 12 тестов: инициализация, валидация, `clean_*` методы,
  `is_clean`, совместимость с `ImmutableMultiDict`.
- `tests/test_views.py` — 11 тестов: HTTP-методы, 405/404, `as_view()`,
  `get_all_urls()`, `is_abort_exception()`.
- `tests/test_url.py` — 10 тестов: `Url`, `make_urls()`, `include()`,
  namespace'ы, endpoint'ы.
- `tests/test_conf.py` — 7 тестов: `DefaultSettings`, `Settings`,
  поведение при отсутствии / невалидном `FLASK_SETTINGS_MODULE`.
- `tests/test_csrf.py` — 8 тестов: `_get_dt_s()`, `csrf_gen_token()`,
  `csrf_check_token()`, `ConfigurationError`, `CSRFError`.
- `tests/test_request.py` — 3 теста: `remote_address` с `HTTP_X_REAL_IP`
  и без него.
- `tests/test_cli.py` — 10 тестов: `token_gen()`, `gen_token()`, уникальность
  токенов, регистрация CLI-команд, `build_proto()`.
- `setup.cfg` — конфигурация pytest (`testpaths`, `python_files` и т.д.).
- `setup.py` — добавлен `extras_require['dev']`: `pytest>=7.0`, `pytest-flask`,
  `coverage`.
- `.github/workflows/test.yml` — CI-матрица: Python 3.9–3.12 × Flask 2.x / 3.x.

### Версия

- Версия повышена с `2.0.0` до `2.1.0`.

---

## [2.0.0] — 2026-04-04

### BREAKING CHANGES — требуется обновление существующих проектов

**Изменён способ инициализации фреймворка.**
Движок больше не создаётся автоматически при импорте `flaskcbv.core`.

**Что нужно обновить в каждом проекте:**

| Файл | Действие |
|------|----------|
| `apps/project.py` | **Обязательно.** Заменить `from flaskcbv.core import engine` на вызов `create_engine()` (см. ниже). |
| `apps/flaskconfig.py` | **Обязательно**, если используется `FormViewMixin`. Убедиться, что задан `SECRET_KEY`. |
| `apps/start.py` | Рекомендуется. Убрать хардкод `debug=True, host='0.0.0.0'`, читать из переменных окружения. |
| `setup.py` / `requirements.txt` | Снять пин `Werkzeug==2.0.0`, указать `Werkzeug>=2.1`. |

Необходимо обновить `project.py` в каждом проекте:

```python
## БЫЛО (1.x):
from flaskcbv.core import engine
application = engine.app

## СТАЛО (2.x):
from flaskcbv.core import create_engine
engine = create_engine()
application = engine.app
```

### Архитектура

- **`flaskcbv/core/__init__.py`** — удалён `engine = CBVCore()` с уровня модуля.
  Добавлена фабричная функция `create_engine(**kwargs)`. Движок теперь создаётся
  явно в `project.py` проекта, что позволяет импортировать фреймворк без немедленного
  создания Flask-приложения и устраняет проблемы с тестированием.

- **`flaskcbv/view/generic.py`** — удалён атрибут класса `__flask = get_flask()`,
  который вычислялся в момент определения класса (до создания движка).
  `View.get_all_urls()` теперь вызывает `get_flask()` лениво при каждом обращении.

- **`flaskcbv/protos/*/apps/project.py`** — шаблоны новых проектов обновлены:
  `from flaskcbv.core import engine` → `from flaskcbv.core import create_engine`.

- **`flaskcbv/protos/*/apps/start.py`** — убран хардкод `debug=True, host='0.0.0.0'`.
  Параметры запуска теперь читаются из переменных окружения:
  `FLASK_DEBUG` (default: false), `FLASK_HOST` (default: 127.0.0.1), `FLASK_PORT` (default: 5000).

- **`flaskcbv/core/base.py`** — `jinja_loader` теперь возвращает пустой `FileSystemLoader`
  вместо `None` при отсутствии настроенных директорий шаблонов, с предупреждением в лог.

### Документация

- `API_RUS.txt` — добавлен раздел «МИГРАЦИЯ С ВЕРСИИ 1.x НА 2.x» с подробными
  инструкциями по обновлению существующих проектов.
- `API_RUS.txt` — описана функция `create_engine()`.

### Версия

- Мажорная версия повышена с `1.6.1` до `2.0.0` в связи с нарушением обратной совместимости.

---

## [1.6.1] — 2026-04-03

### Качество кода

- **`flaskcbv/templatetags/__init__.py`** — удалён отладочный `print(self.environment.extensions)`.

- **`flaskcbv/templates/__init__.py`** — удалён закомментированный `## print(environment.extensions)`.

- **`flaskcbv/conf/__init__.py`** — удалён закомментированный мёртвый блок кода в `BaseSettings.__setattr__`.

- **`flaskcbv/protos/simple/apps/start.py`**, **`flaskcbv/protos/custom/apps/start.py`** —
  удалена закомментированная строка инициализации DEBUG-логгера.

- **`ruff.toml`** — добавлен конфигурационный файл линтера ruff. Включены правила E, F, W, B.
  Игнорируются E265/E266 (двойной `##` — авторский стиль), B006 и B007.
  Для прототипов в `flaskcbv/protos/` ослаблены правила импортов.

- **Все файлы** — однострочные конструкции `try: x` / `except: y` развёрнуты в многострочный
  вид во всех файлах проекта:
  `core/base.py`, `templates/__init__.py`, `scripts/flaskcbv.py`,
  `scripts/commands/initproject.py`, `url/__init__.py`,
  `view/mixins/getargument.py`, `view/mixins/jsonmixin.py`,
  `protos/custom/misc/mixins/__init__.py`.
  Заодно уточнены типы исключений в `core/base.py` (`KeyError`) и
  `templates/__init__.py` (`AttributeError`).

- **`flaskcbv/py.typed`** — добавлен маркер PEP 561, сигнализирующий инструментам
  статической проверки типов (mypy, pyright) о поддержке типизации пакетом.

### Версия

- Версия повышена с `1.6.0` до `1.6.1`.

---

## [1.6.0] — 2026-04-03

### Безопасность

- **`flaskcbv/view/crud.py`** — убран глобальный хардкод секретного ключа
  (`secret_key = 'veryimportantsecretkey'`). Сериализатор CSRF-токенов теперь создаётся
  лениво внутри методов `csrf_gen_token` / `csrf_check_token`, получая ключ через
  `current_app.secret_key` в контексте запроса. Если `SECRET_KEY` не задан в конфиге
  Flask-приложения — выбрасывается `ConfigurationError`.

- **`flaskcbv/view/crud.py`** — заменён удалённый в Werkzeug 2.1 `werkzeug.security.safe_str_cmp`
  на `hmac.compare_digest` из стандартной библиотеки. Сравнение CSRF-токенов теперь
  защищено от timing-атак средствами стандартной библиотеки.

- **`flaskcbv/scripts/commands/initproject.py`**, **`flaskcbv/scripts/common.py`** —
  `random.choice()` заменён на `secrets.choice()` (криптографически стойкий генератор).
  Длина генерируемого `SECRET_KEY` при инициализации проекта увеличена с 30 до 50 символов.

### Совместимость

- **`flaskcbv/core/base.py`** — удалён импорт `flask.helpers.locked_cached_property`,
  удалённый во Flask 2.0. Заменён на `functools.cached_property` из стандартной библиотеки.

- **`setup.py`** — снят жёсткий пин `Werkzeug==2.0.0`. Новые минимальные требования:
  `Flask>=2.0`, `Werkzeug>=2.1`. Убраны закомментированные зависимости. Добавлены
  классификаторы Python 3.9–3.12. Минимальная версия Python повышена до 3.8.

- **`flaskcbv/scripts/cliargs.py`** — `dict.keys()` обёрнут в `list()` при передаче
  в argparse `choices=`, что исправляет несовместимость с Python 3.

- **`flaskcbv/core/__init__.py`** — удалён дублирующийся импорт `namespases`.
  Обработка ошибки импорта `urls.py` унифицирована.

- **`flaskcbv/conf/__init__.py`** — добавлен отсутствовавший `import warnings`.
  Удалена зависимость от пакета `six` (EOL): `six.string_types` заменён на встроенный `str`.

- **`flaskcbv/url/__init__.py`**, **`flaskcbv/core/base.py`** — убраны конструкции
  `raise(Exception(...))` с лишними скобками, заменены на `raise Exception(...)`.

- **`flaskcbv/forms/form.py`** — убраны избыточные вызовы `.keys()` при итерации
  по словарям; `len(self.errors.keys()) == 0` заменён на `not self.errors`.

- **`flaskcbv/core/base.py`** — `get_all_urls()` теперь возвращает `list` вместо
  `dict_keys`-объекта, что соответствует задокументированному поведению ("список всех url").

### Обработка исключений

- **`flaskcbv/exceptions.py`** — добавлен новый модуль с базовыми классами исключений
  фреймворка: `FlaskCBVError`, `ConfigurationError`, `CSRFError`.

- **`flaskcbv/view/crud.py`** — CSRF-ошибки теперь выбрасывают `CSRFError` вместо
  generic `Exception`.

- **`flaskcbv/view/mixins/getargument.py`** — все `bare except` заменены на
  `except KeyError` (единственное ожидаемое исключение при поиске ключа в dict-like объектах).

- **`flaskcbv/view/mixins/jsonmixin.py`** — `bare except` заменены на конкретные типы:
  `AttributeError` при вызове `super().get_context_data()`, `KeyError` при доступе
  к элементам контекста и удалении ключей из ответа.

- **`flaskcbv/url/__init__.py`** — `bare except` заменены на `except Exception`
  при получении endpoint из `url.endpoint`.

- **`flaskcbv/protos/custom/misc/mixins/__init__.py`** — `bare except` заменены на:
  `AttributeError` при доступе к `self.session_id`;
  `(KeyError, ValueError)` при разборе параметра `json_indent`.

- **`flaskcbv/scripts/common.py`** — исправлен недостижимый код в `get_file_path()`:
  проверка `stat.S_ISREG` перенесена за пределы блока `except` и теперь реально выполняется.
  Добавлен недостававший `import stat`. `raise(err)` заменён на `raise`.

### Версия

- Версия повышена с `1.5.6` до `1.6.0`.
