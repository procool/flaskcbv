# FlaskCBV

![Tests](https://github.com/procool/flaskcbv/actions/workflows/test.yml/badge.svg)
![Python versions](https://img.shields.io/pypi/pyversions/flaskcbv)
![PyPI version](https://img.shields.io/pypi/v/flaskcbv)
![License](https://img.shields.io/pypi/l/flaskcbv)

> Английская версия: [README.md](../README.md)  
> Справочник по API: [docs/api_rus.md](api_rus.md)

---

## Совместимость

| FlaskCBV | Python      | Flask     | Werkzeug  |
|----------|-------------|-----------|-----------|
| 2.x      | 3.8 – 3.12  | 2.0 – 3.x | >= 2.1    |
| 1.x      | 3.6 – 3.8   | 1.x       | 2.0.0     |

Обновляетесь с 1.x? См. [руководство по миграции](api_rus.md#миграция-с-версии-1x-на-2x).  
Нужно обновить четыре файла: `apps/project.py` (обязательно), `apps/flaskconfig.py` (обязательно при использовании форм),
`apps/start.py` (рекомендуется), пин версии `Werkzeug` (обязательно).

---

## Введение

FlaskCBV — альтернативный фреймворк для работы с Flask, реализующий подход
«представления на основе классов» (Class-Based Views, CBV).

Платформа позволяет строить чистую архитектуру, в полной мере используя
все преимущества этого подхода.

Фреймворк стилистически близок к Django:
* чтобы упростить его изучение;
* потому что архитектура Django выглядит элегантно.

Цель — минимально нагруженная обёртка над Flask без лишних зависимостей.

---

## Особенности использования

Вместо декоратора `@route` обработчики описываются в `urls.py` со следующими возможностями:
* использование `include` для подключения URL-конфигураций из других приложений;
* разбиение по пространствам имён (`namespace`) для каждого приложения.

Конфигурация фреймворка хранится в модуле `settings`.
Отдельный модуль предусмотрен специально для настроек Flask.

---

## Зависимости

* setuptools
* Flask
* Werkzeug
* Jinja2
* MarkupSafe

---

## Установка и настройка

1. Установите фреймворк через pip:

    ```bash
    pip install flaskcbv
    ```

    Необходимые зависимости установятся автоматически.

2. Создайте директорию проекта:

    ```bash
    mkdir project && cd project
    ```

3. Создайте проект с помощью утилиты flaskcbv:

    ```bash
    flaskcbv initproject
    ```

    Проект будет создан в текущей директории.

4. Создайте директорию для статических файлов:

    ```bash
    mkdir apps/assets
    touch apps/assets/some_test.js
    ```

    Этот файл будет доступен по адресу `http://127.0.0.1:5555/static/some_test.js`.  
    Расположение статики можно изменить в `settings/local.py` через переменные
    `STATIC_PATH` и `STATIC_URL`.

5. Запустите сервер:

    ```bash
    cd apps
    python3 start.py
    ```

    По умолчанию сервер запускается на порту 5555.

6. Проверьте работу через браузер или telnet (в отдельном терминале):

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

---

## Структура директорий

После генерации проекта создаются две директории:

* `apps/` — приложения проекта и модули запуска.
* `settings/` — модуль настроек FlaskCBV.

### Директория `settings/`

| Файл          | Назначение |
|---------------|------------|
| `__init__.py` | Базовые настройки фреймворка. |
| `local.py`    | Подключается из `__init__.py`; содержит настройки, специфичные для конкретного окружения. |

Рекомендуемый подход: базовые настройки (набор приложений, заголовки по умолчанию и т.д.) —
в `__init__.py`; настройки окружения (подключение к БД, пути к шаблонам и т.д.) — в `local.py`.
При переносе проекта на другой стенд достаточно заменить `local.py`.
Файл `__init__.py` удобно хранить в репозитории.

При необходимости всю директорию `settings/` можно заменить одним файлом `settings.py` —
фреймворк это поддерживает.

### Директория `apps/`

| Файл/папка | Назначение |
|------------|------------|
| `start.py` | Запуск сервера в режиме разработки. Автоматически задаёт порт и абсолютный путь к проекту. На его основе легко создать `wsgi.py` для production. |
| `project.py` | Создаёт Flask-приложение через FlaskCBV. |
| `flaskconfig.py` | Конфигурационные переменные Flask. |
| `urls.py` | Описание основных пространств имён и обработчиков проекта. |
| `main/` | Приложение по умолчанию, выводящее `"It works on FlaskCBV!"`. |
| `main/urls.py` | URL-конфигурация приложения `main`, подключается в основной `urls.py`. |
| `main/views.py` | Модуль с `mainView`; здесь же задаётся шаблон для вывода. |
| `main/templates/main/index.tpl` | Шаблон приложения `main`. |

Для корректной работы приложение `main` должно быть указано в кортеже `APPLICATIONS`
в модуле настроек.

---

## Запуск тестов

> Подробная документация по тестам — что покрывает каждый файл, справочник по фикстурам и покрытие — в **[docs/testing_rus.md](testing_rus.md)**.

### Предварительные требования

Установите фреймворк с зависимостями для разработки:

```bash
pip install -e ".[dev]"
```

Это установит `pytest`, `pytest-flask` и `coverage` вместе с основными зависимостями.

---

### Запуск полного набора тестов

Из **корня проекта** (директория, содержащая `setup.py`):

```bash
pytest
```

pytest автоматически обнаружит все тесты согласно конфигурации в `setup.cfg`
(`testpaths = tests`).

---

### Полезные опции pytest

```bash
## Подробный вывод (имя каждого теста):
pytest -v

## Остановиться на первом падении:
pytest -x

## Запустить один файл:
pytest tests/test_forms.py

## Запустить один класс:
pytest tests/test_views.py::TestViewHTTPMethods

## Запустить один тест:
pytest tests/test_csrf.py::TestCsrfCheckToken::test_valid_token_passes

## Показать вывод print:
pytest -s

## Запустить тесты по ключевому слову:
pytest -k "csrf"
```

---

### Отчёт о покрытии

```bash
## Запустить тесты и вывести сводку:
coverage run -m pytest
coverage report

## Сформировать HTML-отчёт (открыть в браузере):
coverage html
open htmlcov/index.html
```

---

### Как устроена тестовая инфраструктура

Тесты находятся в директории `tests/`. Три файла не являются тестами:

| Файл | Назначение |
|------|------------|
| `tests/conftest.py` | Фикстуры pytest (engine, app, client, контексты). |
| `tests/settings.py` | Минимальный модуль настроек для тестов. |
| `tests/urls.py` | Минимальная URL-конфигурация с двумя тестовыми представлениями. |

**Важно:** `conftest.py` добавляет `tests/` в начало `sys.path` и устанавливает
`FLASK_SETTINGS_MODULE=settings` **до** любого импорта из flaskcbv.
Это обязательно, так как `flaskcbv.conf` читает модуль настроек при импорте.

Основные фикстуры `conftest.py`:

| Фикстура | Область | Описание |
|----------|---------|----------|
| `engine` | session | Единственный экземпляр `CBVCore`, общий для всех тестов. |
| `app` | session | Flask-приложение с `TESTING=True` и установленным `SECRET_KEY`. |
| `client` | function | Тестовый клиент Flask (создаётся заново для каждого теста). |
| `app_ctx` | function | Активный контекст приложения. |
| `req_ctx` | function | Активный контекст запроса. |

Фикстуры `engine` и `app` имеют область `session`, чтобы избежать ошибок
повторной регистрации endpoint'ов при пересоздании Flask-приложения.

---

### Что тестируется

| Файл | Покрывает |
|------|-----------|
| `test_forms.py` | Инициализация `Form`, копирование данных, методы `clean_*`, ошибки, `is_clean`, `ImmutableMultiDict`. |
| `test_views.py` | HTTP-методы, 404/405, `as_view()`, `get_all_urls()`, вспомогательные методы для abort. |
| `test_url.py` | `Url`, `make_urls()`, `include()`, пространства имён, endpoint'ы. |
| `test_conf.py` | `DefaultSettings`, `Settings`, поведение при отсутствующем/невалидном `FLASK_SETTINGS_MODULE`. |
| `test_csrf.py` | `_get_dt_s()`, `csrf_gen_token()`, `csrf_check_token()`, `ConfigurationError`, `CSRFError`. |
| `test_request.py` | `remote_address` с заголовком `HTTP_X_REAL_IP` и без него. |
| `test_cli.py` | `token_gen()`, `gen_token()`, уникальность токенов, CLI-команды, `build_proto()`. |

---

### Написание новых тестов

1. Добавьте файл `test_*.py` в директорию `tests/`.
2. Используйте фикстуры из `conftest.py` как аргументы функции:

    ```python
    def test_my_view(client):
        r = client.get('/')
        assert r.status_code == 200
    ```

3. Для тестов, требующих контекст приложения или запроса без HTTP-вызовов,
   используйте `app_ctx` или `req_ctx`:

    ```python
    def test_something_in_context(app_ctx):
        from flask import current_app
        assert current_app.config['TESTING'] is True
    ```

4. Если нужен новый тестовый маршрут — добавьте его в `tests/urls.py`.

5. Если нужны другие настройки — используйте `monkeypatch` для `os.environ`
   и создайте `Settings()` напрямую, **не изменяя** `tests/settings.py`,
   так как этот файл используется всеми тестами.

---

## Примеры FlaskCBV

### Простой JSON-сервер

```python
from flaskcbv.response import Response
from flaskcbv.view.mixins import JSONMixin
from flaskcbv.view import View


class JSONView(JSONMixin, View):
    def get_json_indent(self):
        return self.__json_indent

    def dispatch(self, request, *args, **kwargs):
        try:
            self.__json_indent = int(request.args['json_indent'])
        except (KeyError, ValueError):
            self.__json_indent = None

        r = super(JSONView, self).dispatch(request, *args, **kwargs)

        ## Вернуть контекст как JSON
        return Response(self.get_as_json())


class myJsonView(JSONView):
    def get_context_data(self, **kwargs):
        return {'some': 'var'}


"""
При обработке myJsonView клиент получит:
{
    "errno": 0,
    "error": "OK",
    "details": "",
    "some": "var"
}
"""
```

---

### Проверка сессии пользователя (LoginRequiredMixin)

```python
import logging

import werkzeug.exceptions as ex
from flask import request, session, abort

from flaskcbv.view.mixins import JSONMixin, getArgumentMixin
from flaskcbv.response import Response

from .models import Auth


## Примесь с методами проверки сессии:
class AuthedMixin(object):

    def test_for_user(self):
        ## Попытаться получить сессию из параметров запроса:
        try:
            session_ = self.request.args['session']
        except KeyError:
            session_ = None

        ## Попытаться получить сессию из flask.session (cookie):
        if session_ is None:
            try:
                session_ = session['session']
            except KeyError:
                session_ = None

        ## Сессия не найдена — вернуть 401:
        if session_ is None:
            abort(401)

        ## Проверить сессию, найти пользователя:
        try:
            request.user = Auth.session(session_)
            session['session'] = session_
        except Exception as err:
            request.user = None


## Примесь проверки сессии
class _LoginRequiredMixin(object):
    def prepare(self, *args, **kwargs):
        ## Единственный допустимый тип исключения — abort
        self.test_for_user()

        ## Сессия найдена, но некорректна (или пользователь не найден):
        if request.user is None:
            abort(403)

        return super(_LoginRequiredMixin, self).prepare(*args, **kwargs)


class LoginRequiredMixin(_LoginRequiredMixin, AuthedMixin):
    pass
```

Подмешав `LoginRequiredMixin` в любое представление, перед вызовом `dispatch`
будет выполнена проверка сессии.

---

### Передача переменных контекста в шаблон

```python
import logging
import datetime

from flaskcbv.view import TemplateView
from settings import STATIC_URL


## Примесь, передающая переменные из настроек в контекст
class defaultSettingsMixin(object):

    def get_context_data(self, **kwargs):
        context = super(defaultSettingsMixin, self).get_context_data(**kwargs)
        context['STATIC_URL'] = STATIC_URL
        return context


class myTemplateView(defaultSettingsMixin, TemplateView):
    pass
```

При наследовании от `myTemplateView` в контексте шаблона автоматически
будет присутствовать `STATIC_URL` из настроек.

---

### Шаблонный тег (расширение Jinja2)

Классы шаблонных тегов размещаются в директории `templatetags` в корне проекта.

```bash
cd myproject
mkdir templatetags && cd templatetags
touch __init__.py
```

Пример `mytags.py`:

```python
## encoding: utf8
from jinja2 import nodes
from jinja2.ext import Extension


## Расширение возвращает тип указанного атрибута заданного объекта
class ObjectAttrTypeExtension(Extension):
    ## Если атрибут не задан, False или None — расширение не регистрируется
    enabled = True

    tags = set(['attrtype'])

    def __init__(self, environment):
        super(ObjectAttrTypeExtension, self).__init__(environment)
        environment.extend(
            fragment_cache_prefix='',
            fragment_cache=None
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
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
        except Exception:
            pass
        return u''
```

При запуске FlaskCBV автоматически загрузит тег, и он станет доступен в шаблонах:

```jinja
{% attrtype request, 'method' %}
```

Вернёт: `<class 'str'>`

Подробнее о расширениях Jinja2: https://jinja.palletsprojects.com/en/3.x/extensions/

---

### Пример работы с формами

```python
## Простая форма:
from flaskcbv.forms import Form

class myFormClass(Form):
    def clean_test_passed(self, val):
        ## self.cleaned_data['test_passed'] будет равно 'passed'
        ## self.data['test_passed'] будет равно val
        return 'passed'

    def clean_test_error(self, val):
        ## self.data['test_error'] будет равно val
        ## в self.cleaned_data ключа 'test_error' не будет
        ## self.errors['test_error'] будет содержать исключение 'Some Error'
        raise Exception('Some Error')


from flaskcbv.view.crud import FormViewMixin
from flaskcbv.view import TemplateView


class myFormView(FormViewMixin, TemplateView):
    template = 'index/some.tpl'
    form_class = myFormClass

    ## Раскомментируйте, если нужен редирект по умолчанию:
    #form_success_url = '/action/success/'
    #form_unsuccess_url = '/action/unsuccess/'

    ## Кастомный URL для успешной отправки:
    #def get_from_success_url(self):
    #    return "/some/other/success/url"

    ## При GET клиент получает шаблон, в контексте которого доступна
    ## переменная 'form' с очищенными значениями полей.

    ## Переопределим обработку POST:
    def post(self, *args, **kwargs):

        ## Создать объект формы:
        form = self.get_form()

        ## Проверить форму — запустит form.clean(), который вызовет
        ## методы clean_ATTR, как в Django:
        if form.validate():
            ## По умолчанию — редирект на form_success_url
            ## или self.get_from_success_url():
            return self.form_valid(form)

        else:
            ## По умолчанию — вернуть шаблон с переменной контекста 'form':
            return self.form_invalid(form)
```

---

Удачи в разработке! :)

regards, procool@
