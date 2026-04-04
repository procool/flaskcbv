# TODO

- [ ] переименовать AVALIBLE_METHODS -> AVAILABLE_METHODS (breaking, мажорная версия)
- [ ] Response.render(headers={}) и Form.__init__(data={}) - мутируемые дефолты, поправить
- [ ] itsdangerous добавить в install_requires (setup.py)
- [ ] from urls import namespases - кривой импорт, переделать на importlib
- [ ] startapp в cli - заглушка, либо реализовать либо убрать
- [ ] make_urls мутирует входные Url объекты - надо чинить
- [ ] validate() не идемпотентен - очищать errors/cleaned_data в начале clean()
- [ ] X-Real-IP доверяем без проверки - добавить TRUSTED_PROXIES
- [ ] CSRF_TOKEN_MAX_AGE вынести в настройки
- [ ] __version__ не экспортируется из пакета
- [ ] тесты: поднять порог с 60% до 75%+
- [ ] тесты: Response (callable, generator, заголовки), JSONMixin include/exclude, TemplateIsAjaxView
- [ ] ruff добавить в dev зависимости
