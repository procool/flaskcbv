import os, sys, stat
import logging

def get_templatetags(dirname):
    for path in sys.path:
        p = "/".join((path, dirname))
        if os.path.exists(p):
            return p


def register_tag(environment, dirpath, name):
    name_ = "%s.%s" % (dirpath, name)
    mod_ = getattr(__import__(name_), name)
    for extension in dir(mod_):
        extension = getattr(mod_, extension)
        if not hasattr(extension, 'enabled'):
            continue
        if not extension.enabled:
            continue
        environment.add_extension(extension)
        ## print environment.extensions


def register_tags(environment):
    dirpath = 'templatetags'
    path_ = get_templatetags(dirpath)
    try:
        for name in os.listdir(path_):
            fpath = os.path.abspath("/".join((path_, name)))
            fstat = os.stat(fpath)

            if not stat.S_ISREG(fstat.st_mode):
                continue

            name = name[0:-3]
            try: register_tag(environment, dirpath, name)
            except: pass
    except Exception as err:
        logging.error('Error on register templatetags with path "%s": %s' % (path_, err))
