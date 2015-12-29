
class cmdStartApp(object):
    def get_cli_commands(self):
        commands = super(cmdStartApp, self).get_cli_commands()
        commands['startapp'] = self.__main
        return commands

    def __main(self):
        print "Starting application"

