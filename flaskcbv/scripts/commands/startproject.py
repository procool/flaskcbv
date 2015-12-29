
class cmdStartProject(object):
    def get_cli_commands(self):
        commands = super(cmdStartProject, self).get_cli_commands()
        commands['startproject'] = self.__main
        return commands

    def __main(self):
        print "OOOOO"

