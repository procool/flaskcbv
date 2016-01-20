from flaskcbv.core import engine

application = engine.app
application.secret_key = '{{ SECRET_KEY }}'


