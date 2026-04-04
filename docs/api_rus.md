# FlaskCBV — Справочник по API

> Английская версия: [docs/api.md](api.md)

---

## Требования

| Компонент | Версия  |
|-----------|---------|
| Python    | >= 3.8  |
| Flask     | >= 2.0  |
| Werkzeug  | >= 2.1  |

---

## flaskcbv.core — Инициализация движка

### `create_engine(**kwargs)`

Фабричная функция, создающая и возвращающая экземпляр `CBVCore`.
Начиная с версии 2.0.0 движок **обязательно создавать явно** в `project.py`
после установки переменной окружения `FLASK_SETTINGS_MODULE`.

```python
from flaskcbv.core import create_engine

engine = create_engine()
application = engine.app
application.secret_key = 'your-secret-key'
```

**Аргументы:** `**kwargs` — переопределяют любые параметры, переданные конструктору `Flask`.  
**Возвращает:** экземпляр `CBVCore` с готовым к работе атрибутом `.app`.

---

### `class CBVCore`

Центральный движок фреймворка. Читает настройки, создаёт singleton-экземпляр Flask,
регистрирует URL-правила из `urls.namespases` и загружает шаблонные теги.

| Атрибут | Описание |
|---------|----------|
| `app`   | Экземпляр `Flask`. |
| `views` | Список зарегистрированных объектов-представлений. |

---

## flaskcbv.url — Маршрутизация

### `class Url(url, obj, name=None, namespace=None)`

Связывает URL-путь с представлением.

```python
Url('/users/<int:id>', UserView(), name='user_detail')
```

| Параметр    | Описание |
|-------------|----------|
| `url`       | Строка URL, например `'/users/<int:id>'`. |
| `obj`       | Экземпляр `View`, результат `as_view()` или результат `include()`. |
| `name`      | Имя endpoint'а для `url_for()`. Обязательно, если `obj` — не `include()`. |
| `namespace` | Устанавливается автоматически через `include()`. |

**Свойство `endpoint`** — возвращает `'namespace:name'` или `'name'`.  
Бросает `Exception`, если `name` не был задан.

---

### `make_urls(*namespases)`

Формирует таблицу URL для `CBVCore`. Вызывается в `urls.py` проекта,
результат присваивается переменной `namespases`.

```python
from flaskcbv.url import Url, make_urls

namespases = make_urls(
    Url('/',      IndexView(), name='index'),
    Url('/about', AboutView(), name='about'),
)
```

---

### `include(namespases, namespace=None, description=None)`

Подключает URL-список под-приложения в указанном пространстве имён.

```python
from apps.blog import urls as blog_urls

namespases = make_urls(
    Url('/blog', include(blog_urls.namespases, namespace='blog')),
)
```

---

## flaskcbv.view — Представления

### `class View`

Базовый класс представления. HTTP-методы определяются как методы экземпляра:

```python
from flaskcbv.view import View
from flaskcbv.response import Response

class MyView(View):
    def get(self, request, *args, **kwargs):
        return Response('Hello')

    def post(self, request, *args, **kwargs):
        return Response('Posted')
```

**Атрибуты и методы:**

| Имя | Описание |
|-----|----------|
| `AVAILABLE_METHODS` | Список разрешённых HTTP-методов. На остальные вернётся 405. По умолчанию: `["GET", "POST", "OPTIONS", "HEAD"]`. |
| `AVALIBLE_METHODS` | **Устарело.** Псевдоним для `AVAILABLE_METHODS`, синхронизируется автоматически. Будет удалён в следующей мажорной версии. |
| `options` | Дополнительные kwargs для `add_url_rule()`. |
| `decorators` | Декораторы уровня представления, применяемые в `as_view()`. |
| `request` | Текущий объект `flask.Request`. |
| `session` | Текущий объект `flask.session`. |
| `prepare(*args, **kwargs)` | Точка входа, вызываемая Flask при каждом запросе. |
| `dispatch(request, *args, **kwargs)` | Определяет HTTP-метод запроса и вызывает соответствующий обработчик (`get`, `post`, …). Возвращает экземпляр `Response`. |
| `get_headers(**kwargs)` | Переопределите для добавления кастомных заголовков ответа. |
| `get_current_url()` | Возвращает URL-путь данного представления. |
| `get_all_urls(**kwargs)` | Возвращает список всех зарегистрированных имён endpoint'ов. |
| `is_abort_exception(ex)` | `True`, если `ex` — HTTP-исключение werkzeug. |
| `test_abort_exception(ex)` | Повторно бросает `ex`, если оно является HTTP-исключением. |

---

### `class TemplateView`

Наследует `View`, добавляет рендеринг Jinja2-шаблонов.

```python
from flaskcbv.view import TemplateView

class HomeView(TemplateView):
    template = 'home/index.tpl'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Home'
        return ctx
```

**Методы:**

| Имя | Описание |
|-----|----------|
| `template` | Путь к Jinja2-шаблону. |
| `get_template_name()` | Возвращает путь к шаблону; переопределите для динамического вычисления. |
| `get_context_data(**kwargs)` | Возвращает словарь переменных шаблона. Автоматически добавляет `request`. |
| `render_template(*args, **kwargs)` | Рендерит шаблон и возвращает HTML-строку. |

---

### `class TemplateIsAjaxView`

Наследует `TemplateView`. Для AJAX-запросов отдаёт шаблон `index-ajax.tpl`,
для обычных — `index.tpl` (и наоборот для шаблонов с суффиксом `-ajax`).

---

## flaskcbv.view.crud — Работа с формами

### `class FormMixin`

Добавляет к представлению инстанцирование формы и CSRF-защиту.

| Атрибут | Описание |
|---------|----------|
| `form_class` | Подкласс `Form` для использования. |
| `form_success_url` | URL для редиректа после успешной отправки формы. |
| `form_unsuccess_url` | URL для редиректа при ошибке валидации. |

**Методы:**

| Имя | Описание |
|-----|----------|
| `get_form(form_class, instance, **kwargs)` | Создаёт и возвращает экземпляр формы. |
| `form_valid(form)` | Вызывается при успешной валидации. По умолчанию — редирект на `form_success_url`. |
| `form_invalid(form)` | Вызывается при ошибке. По умолчанию — редирект на `form_unsuccess_url`. |
| `csrf_gen_token(context)` | Генерирует подписанный CSRF-токен и сохраняет его в сессии. |
| `csrf_check_token(form)` | Проверяет CSRF-токен. Бросает `CSRFError` при ошибке. |

---

### `class FormViewMixin(FormMixin)`

Объединяет `FormMixin` с автоматикой `TemplateView`.

- **GET** — добавляет `form` и `csrf_token` в контекст шаблона.
- **POST** — валидирует форму, вызывает `form_valid()` или `form_invalid()`.

```python
from flaskcbv.view.crud import FormViewMixin
from flaskcbv.view import TemplateView

class ContactView(FormViewMixin, TemplateView):
    template = 'contact.tpl'
    form_class = ContactForm
    form_success_url = '/thank-you/'
```

| Атрибут | Описание |
|---------|----------|
| `csrf_check` | Включить CSRF-валидацию на POST. По умолчанию `True`. |

---

## flaskcbv.view.mixins — Примеси

### `class getArgumentMixin`

Предоставляет единый интерфейс для получения параметров запроса из GET, POST,
cookies и сессии.

```python
value = self.get_argument_smart('user_id', as_get=True, as_post=True)
```

Бросает `KeyError`, если ключ не найден ни в одном из включённых источников.

Источники проверяются в порядке: GET → POST → cookie → session.

---

### `class JSONMixin`

Сериализует результат `get_context_data()` в JSON-ответ.

```python
class MyAPI(JSONMixin, View):
    def dispatch(self, request, *args, **kwargs):
        return Response(self.get_as_json())
```

| Метод | Описание |
|-------|----------|
| `get_as_json(**data)` | Возвращает JSON-строку из контекста + `data`. |
| `json_error(errno, error, details)` | Возвращает JSON с описанием ошибки. |
| `json_response_include()` | Список ключей контекста для включения в ответ (по умолчанию — все). |
| `json_response_exclude()` | Список исключаемых ключей. По умолчанию: `['request']`. |
| `get_json_indent()` | Переопределите для красивой печати JSON. По умолчанию: `None`. |

Структура ответа по умолчанию:

```json
{
    "errno": 0,
    "error": "Ok",
    "details": "",
    "...": "ключи контекста представления"
}
```

При ошибке `get_context_data()`:

```json
{
    "errno": -1,
    "error": "Failed",
    "details": "текст ошибки"
}
```

---

## flaskcbv.forms — Формы

### `class Form`

Базовая форма с Django-подобной валидацией через `clean_<field>()`.

```python
from flaskcbv.forms import Form

class LoginForm(Form):
    def clean_username(self, value):
        if not value:
            raise ValueError('Username is required')
        return value.strip()
```

| Атрибут | Описание |
|---------|----------|
| `raw_data` | Исходный словарь данных (может быть `ImmutableMultiDict`). |
| `data` | Поверхностная копия в виде обычного `dict`. |
| `cleaned_data` | Проверенные значения после `clean()`. |
| `errors` | Словарь `имя_поля → сообщение_об_ошибке` для полей с ошибками. |

| Метод | Описание |
|-------|----------|
| `validate()` | Запускает `clean()` и возвращает `is_clean`. |
| `clean()` | Последовательно вызывает все методы `clean_<field>()`. |
| `is_clean` | `True`, если `errors` пуст. |

---

## flaskcbv.request — Запрос

### `class Request`

Расширенный объект Flask-запроса. Используется всеми представлениями автоматически.

| Свойство | Описание |
|----------|----------|
| `remote_address` | IP-адрес клиента из заголовка `HTTP_X_REAL_IP` или из `REMOTE_ADDR`. |
| `is_ajax` | `True`, если присутствует заголовок `X-Requested-With: XMLHttpRequest`. |

---

## flaskcbv.response — Ответ

### `class Response`

```python
from flaskcbv.response import Response

return Response('Hello, world!')
return Response(lambda: generate_data())   ## callable
return Response(iter_chunks())              ## потоковая передача
```

| Метод | Описание |
|-------|----------|
| `add_header(name, value)` | Добавить кастомный заголовок в ответ. |
| `render(headers={})` | Собрать и вернуть `flask.Response`. |

---

### `class ResponseRedirect`

```python
from flaskcbv.response import ResponseRedirect

return ResponseRedirect('/login/', code=302)
```

---

## flaskcbv.exceptions — Исключения

| Класс | Описание |
|-------|----------|
| `FlaskCBVError` | Базовый класс всех исключений фреймворка. |
| `ConfigurationError` | Ошибка конфигурации (например, отсутствует `SECRET_KEY`). |
| `CSRFError` | Ошибка CSRF-проверки (неверный, просроченный или отсутствующий токен). |

---

## flaskcbv.conf — Настройки

Настройки загружаются из модуля, имя которого задано в переменной окружения
`FLASK_SETTINGS_MODULE`. Незаданные значения берутся из `DefaultSettings`.

```python
from flaskcbv.conf import settings

print(settings.STATIC_URL)   ## '/static'
```

**Значения по умолчанию** (`flaskcbv.conf.defaults.DefaultSettings`):

| Настройка | По умолчанию |
|-----------|-------------|
| `TEMPLATE_PATH` | `'templates'` |
| `STATIC_PATH` | `'static'` |
| `STATIC_URL` | `'/static'` |
| `DEFAULT_HEADERS` | `{}` |

**Обязательные настройки в вашем модуле settings:**

| Настройка | Описание |
|-----------|----------|
| `APPLICATIONS` | Кортеж путей к директориям приложений — по ним строится список мест поиска шаблонов. |
| `FLASKCONFIG` | Имя модуля с конфигурацией Flask (необязательно). **Важно:** Flask-приложение обязано задавать `SECRET_KEY`. Без него CSRF-защита выбросит `ConfigurationError`. |

---

## Схема работы фреймворка

### Запуск

1. Читает имя модуля настроек из переменной окружения `FLASK_SETTINGS_MODULE`.
2. Через `flaskcbv.conf.Settings` создаёт singleton `settings` с параметрами проекта
   в виде атрибутов (все имена — в верхнем регистре).
3. Создаёт экземпляр `flaskcbv.core.base.Flask` (наследник `flask.Flask`),
   настраивает пути к шаблонам и инициализирует `jinja_loader`.
4. Обрабатывает `urls.py`: для каждого URL вызывает `add_url_rule`.
5. Находит и регистрирует шаблонные теги через `flaskcbv.templates.register_tags`.

### Обработка запроса

1. Flask вызывает `prepare()` у нужного класса представления.
2. `prepare()` вызывает `dispatch()`, который определяет HTTP-метод и делегирует
   соответствующему обработчику (`get`, `post`, …).
3. Обработчик возвращает экземпляр `flaskcbv.Response`.
4. `prepare()` вызывает `render()` у полученного объекта и отдаёт результат Flask.

---

## Тестирование

Установка зависимостей для разработки:

```bash
pip install -e ".[dev]"
```

Запуск полного набора тестов из корня проекта:

```bash
pytest
```

Полезные опции:

```bash
pytest -v                                          ## подробный вывод
pytest -x                                          ## остановиться на первом падении
pytest tests/test_forms.py                         ## один файл
pytest tests/test_views.py::TestViewHTTPMethods    ## один класс
pytest -k "csrf"                                   ## по ключевому слову
```

Покрытие кода:

```bash
coverage run -m pytest
coverage report
coverage html && open htmlcov/index.html
```

Полное описание тестовой инфраструктуры — в разделе «Running Tests»
в [README.md](../README.md) или в [русскоязычном переводе](readme_rus.md).

---

## Миграция с версии 1.x на 2.x

В версии 2.0.0 движок больше **не создаётся автоматически** при импорте `flaskcbv.core`.

**Что нужно обновить в каждом проекте:**

| Файл | Действие |
|------|----------|
| `apps/project.py` | **Обязательно.** Заменить `from flaskcbv.core import engine` на вызов `create_engine()` (см. ниже). |
| `apps/flaskconfig.py` | **Обязательно**, если используется `FormViewMixin`. Убедиться, что задан `SECRET_KEY`. |
| `apps/start.py` | Рекомендуется. Убрать хардкод `debug=True, host='0.0.0.0'`, читать из переменных окружения. |
| `setup.py` / `requirements.txt` | Снять пин `Werkzeug==2.0.0`, указать `Werkzeug>=2.1`. |

Обновите `project.py` в каждом существующем проекте:

```python
## БЫЛО (flaskcbv 1.x):
from flaskcbv.core import engine
application = engine.app

## СТАЛО (flaskcbv 2.x):
from flaskcbv.core import create_engine
engine = create_engine()
application = engine.app
```

Рекомендуемое обновление `start.py` — замените хардкод параметров запуска:

```python
## БЫЛО:
application.run(debug=True, host='0.0.0.0', port=5555)

## СТАЛО:
import os
debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
host  = os.environ.get('FLASK_HOST', '127.0.0.1')
port  = int(os.environ.get('FLASK_PORT', '5000'))
application.run(debug=debug, host=host, port=port)
```

Переменные окружения для управления запуском:

| Переменная    | По умолчанию  | Описание |
|---------------|---------------|----------|
| `FLASK_DEBUG` | `'false'`     | Включить debug-режим (`'true'` / `'false'`). |
| `FLASK_HOST`  | `'127.0.0.1'` | Адрес для прослушивания. |
| `FLASK_PORT`  | `'5000'`      | Порт. |
