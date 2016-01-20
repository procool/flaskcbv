import logging
import sys
from common import CommonMixin
from cliargs import CliArgs
from commands.initproject import cmdInitProject
from commands.startapp import cmdStartApp

## Main wrapper class of this program:
class FlaskCBV(cmdInitProject, cmdStartApp, CommonMixin, CliArgs):

    ## Method called when all command line arguments are readed:
    def run(self):
        logging.debug("Runned!")

        self.cli_action_def()

        logging.debug("Done!")


def main():
    ## Create program object, and call command line arguments processing:
    o = FlaskCBV()
    try: o.cli()
    except Exception as err:
        logging.critical("%s" % err)
        o.log_traceback()
        sys.exit(1)

if __name__ == '__main__':
    main()
