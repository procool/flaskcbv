# -*- coding: utf-8 -*-

import os, sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

sys.path.append('{{ WEB }}')
sys.path.append('{{ APPS }}')

os.environ.setdefault("FLASK_SETTINGS_MODULE", "settings")

from project import application

if __name__ == "__main__":
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    host  = os.environ.get('FLASK_HOST', '127.0.0.1')
    port  = int(os.environ.get('FLASK_PORT', '5000'))
    application.run(debug=debug, host=host, port=port)

