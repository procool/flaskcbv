import os, sys
import string, random
from jinja2 import Environment, FileSystemLoader


class cmdInitProject(object):
    protos_dir_name = 'protos/simple'

    def get_cli_commands(self):
        commands = super(cmdInitProject, self).get_cli_commands()
        commands['initproject'] = self.__main
        return commands

    def get_protos_dir(self):
        if hasattr(self, '__protos_dir'):
            return getattr(self, '__protos_dir')
        for path in sys.path:
            p = "/".join((path, 'flaskcbv', self.protos_dir_name))
            if os.path.exists(p):
                setattr(self, '__protos_dir', p)
                return self.get_protos_dir()
        raise Exception('FlaskCBV Protos is not found!')

    def get_proto_template(self, tpl):
        return self.get_jinja().get_template(tpl)
        

    def get_jinja(self):
        if hasattr(self, '__jinja'):
            return getattr(self, '__jinja')
        setattr(self, '__jinja', Environment(
            auto_reload=True,
            loader=FileSystemLoader(self.get_protos_dir(), encoding='utf-8',),
        ))
        return self.get_jinja()


    @staticmethod
    def gen_token(size):
        chars=string.ascii_uppercase + string.digits + string.hexdigits + string.ascii_lowercase + '$,/[]'
        return ''.join(random.choice(chars) for _ in range(size))


    def get_render_params(self):
        return {
            'WEB': os.path.abspath('.'),
            'APPS': '%s/apps' % os.path.abspath('.'),
            'SECRET_KEY' : self.gen_token(30)
        }

    def build_proto(self, tpl, **params):
        template_ = self.get_proto_template(tpl)

        newpath = os.path.abspath(tpl)
        if os.path.exists(newpath):
            raise Exception('Path allready exist: %s; May be existing project?!' % newpath)
        newdir = os.path.dirname(newpath)
        try: os.makedirs(newdir)
        except OSError as err:
            if not err.errno in (17,):
                raise err
        proto_ = open(newpath, 'w')
        proto_.write( template_.render(**params) )
        proto_.close()



    def __main(self):
        params = self.get_render_params()
        self.build_proto('settings/__init__.py', **params)
        self.build_proto('settings/local.py', **params)
        self.build_proto('apps/__init__.py', **params)
        self.build_proto('apps/start.py', **params)
        self.build_proto('apps/project.py', **params)
        self.build_proto('apps/flaskconfig.py', **params)
        self.build_proto('apps/urls.py', **params)
        self.build_proto('apps/main/__init__.py', **params)
        self.build_proto('apps/main/urls.py', **params)
        self.build_proto('apps/main/views.py', **params)
        self.build_proto('apps/main/templates/main/index.tpl', **params)


            
        print "Done!"

