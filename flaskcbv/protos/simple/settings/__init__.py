FLASKCONFIG = 'flaskconfig'

APPLICATIONS = (
    'main', 
)

DEFAULT_HEADERS = {
    'server' : 'my WEB Server',
}

try:
    from local import *
except Exception as err:
    pass

