from flaskcbv.core import create_engine

engine = create_engine()
application = engine.app
application.secret_key = '{{ SECRET_KEY }}'


