# Changelog

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
