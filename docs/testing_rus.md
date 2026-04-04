# Тестирование

> English version: [docs/testing.md](testing.md)

---

## Быстрый старт

Установка с зависимостями для разработки:

```bash
pip install -e ".[dev]"
```

Запуск всех тестов:

```bash
pytest
```

---

## Запуск отдельных тестов

```bash
pytest -v                                              # подробный вывод: имя каждого теста
pytest -x                                             # остановиться на первом падении
pytest -s                                             # показать print/log вывод
pytest -k "csrf"                                      # фильтр по ключевому слову
pytest tests/test_forms.py                            # один файл
pytest tests/test_views.py::TestViewHTTPMethods       # один класс
pytest tests/test_csrf.py::TestCsrfCheckToken::test_valid_token_passes  # один тест
```

---

## Покрытие

```bash
coverage run -m pytest
coverage report                    # сводка в терминале
coverage html && open htmlcov/index.html   # HTML-отчёт
```

Текущее суммарное покрытие: **84%**.  
CI требует не менее **75%** (`--fail-under=75` в `.github/workflows/test.yml`).

---

## Инфраструктура тестов

В директории `tests/` есть три вспомогательных файла, которые не являются тест-файлами:

| Файл | Назначение |
|------|-----------|
| `tests/conftest.py` | pytest-фикстуры, общие для всех тестов |
| `tests/settings.py` | Минимальный модуль настроек flaskcbv для тестов |
| `tests/urls.py` | Минимальная конфигурация URL с двумя вьюхами (`/` и `/about`) |

### Фикстуры (`conftest.py`)

| Фикстура | Область | Описание |
|----------|---------|----------|
| `engine` | session | Один экземпляр `CBVCore` на весь прогон тестов |
| `app` | session | Flask test app с `TESTING=True` и установленным `SECRET_KEY` |
| `client` | function | Flask test client — для HTTP-уровневых тестов |
| `app_ctx` | function | Активный контекст приложения — когда нужен `current_app` |
| `req_ctx` | function | Активный контекст запроса — когда нужен `flask.request` |

**Правило выбора фикстуры:**
- Тестирование HTTP-ответов → `client`
- Тестирование методов вьюх / объектов Response → `req_ctx`
- Тестирование регистрации URL / `get_all_urls()` → `app_ctx`

---

## Тест-файлы

### `test_views.py` — Вьюхи (26 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestViewHTTPMethods` | GET/POST возвращают 200, неизвестный метод — 405, несуществующий маршрут — 404 |
| `TestViewAsView` | `as_view()` возвращает callable, устанавливает `__name__`, `view_class`, `AVAILABLE_METHODS` |
| `TestViewOptionsIsolation` | Класс-атрибут `options` не мутируется при `__init__`; каждый экземпляр получает свою копию |
| `TestViewMethodsAlias` | Синхронизация `AVAILABLE_METHODS` ↔ `AVALIBLE_METHODS` через `__init_subclass__`; алиасы в базовом классе — один объект |
| `TestTemplateIsAjaxView` | Выбор шаблона для ajax/не-ajax запросов; инвертированные имена с `-ajax`; явный параметр `is_ajax` |
| `TestViewGetAllUrls` | `get_all_urls()` возвращает список с зарегистрированными эндпоинтами |
| `TestViewAbortException` | `is_abort_exception` / `test_abort_exception` определяют и пробрасывают HTTP-исключения |

### `test_response.py` — Response (13 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestResponseString` | Строковое тело, пустая строка, статус 200 |
| `TestResponseCallable` | Callable вызывается в момент рендера, а не при создании; поддержка лямбд |
| `TestResponseGenerator` | Генератор стримится корректно; все части присутствуют в теле ответа |
| `TestResponseHeaders` | `add_header()` сохраняется; появляется в ответе; `render(headers=)` мержится |
| `TestResponseRedirect` | 302 по умолчанию, кастомный код (301), заголовки пробрасываются |

### `test_jsonmixin.py` — JSONMixin (13 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestJSONMixinEnvelope` | Стандартный конверт `errno/error/details`; мерж контекста; extra kwargs; валидный JSON |
| `TestJSONMixinInclude` | `json_response_include()` фильтрует ключи; отсутствующие ключи игнорируются; `None` означает все ключи |
| `TestJSONMixinExclude` | По умолчанию исключает `request`; кастомный список; отсутствующий ключ в exclude игнорируется |
| `TestJSONMixinError` | `json_error()` с дефолтными и кастомными полями; исключение в `get_context_data` возвращает error-конверт |

### `test_forms.py` — Формы (11 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestFormInit` | Пустые данные, копирование из raw dict, совместимость с `ImmutableMultiDict` |
| `TestFormValidation` | Валидные/невалидные данные, методы `clean_*`, наполнение `cleaned_data`, накопление ошибок, флаг `is_clean` |

### `test_csrf.py` — CSRF-защита (10 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestGetDtS` | Исключение без `SECRET_KEY`; возвращает сериализатор; использует ключ приложения |
| `TestCsrfGenToken` | Токен сохраняется в сессию; возвращается строкой; идемпотентен в рамках сессии |
| `TestCsrfCheckToken` | Валидный токен проходит; отсутствие токена в сессии/форме бросает исключение; неверный токен бросает `CSRFError` |

### `test_request.py` — Request (6 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestRemoteAddressUntrusted` | `X-Real-IP` игнорируется при пустом `TRUSTED_PROXIES`; неизвестный peer не доверенный |
| `TestRemoteAddressTrusted` | `X-Real-IP` используется если peer в `TRUSTED_PROXIES`; фолбэк при отсутствии заголовка; список из нескольких прокси |

### `test_url.py` — URL-маршрутизация (11 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestUrlClass` | `Url` хранит путь/имя; `endpoint` с неймспейсом и без; исключение без имени |
| `TestMakeUrls` | Возвращает список; структура из 5 элементов на запись; несколько URL |
| `TestInclude` | `include()` устанавливает неймспейс на все записи; обновляет строку эндпоинта |

### `test_conf.py` — Настройки (9 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestDefaultSettings` | Все дефолтные значения присутствуют (`TEMPLATE_PATH`, `STATIC_PATH`, `STATIC_URL`, `DEFAULT_HEADERS`) |
| `TestSettings` | Атрибут модуля установлен; значения читаются из модуля; дефолты применяются для отсутствующих ключей; исключение без env var; исключение при неверном имени модуля |

### `test_cli.py` — CLI-команды (18 тестов)

| Класс | Что проверяется |
|-------|----------------|
| `TestTokenGen` | `CommonMixin.token_gen()` длина, набор символов, кэширование |
| `TestGenToken` | `cmdInitProject.gen_token()` длина, тип, уникальность |
| `TestGetCliCommands` | `initproject` зарегистрирован и вызываемый |
| `TestStartApp` | `startapp` зарегистрирован; создаёт нужные файлы; имя приложения в `views.py`; исключение без имени; исключение если директория существует |
| `TestInitProject` | `build_proto` создаёт файл по шаблону; исключение если файл уже существует |

---

## Покрытие по модулям

| Модуль | Покрытие | Примечания |
|--------|----------|-----------|
| `response.py` | 98% | |
| `jsonmixin.py` | 100% | |
| `exceptions.py` | 100% | |
| `forms/form.py` | 86% | |
| `view/generic.py` | 77% | Рендеринг `TemplateView` не покрыт (нужны реальные шаблоны) |
| `view/crud.py` | 56% | POST-поток `FormViewMixin` не покрыт |
| `scripts/cliargs.py` | 42% | Полный цикл разбора аргументов CLI не тестируется |
| `templates/__init__.py` | 25% | Регистрация тег-функций не покрыта |
| `view/mixins/getargument.py` | 22% | `GetArgumentMixin` не покрыт |
