import sys
import argparse
import logging


class CliArgs(object):
    __datefmt = '[%d/%b/%Y %H:%M:%S]'
    __format  = '%(asctime)s %(levelname)s: %(message)s'


    def get_cli_commands(self):
        return {}

    def get_cli_command(self):
        return self.__action

    @property
    def cli_action_def(self):
        return self.get_cli_commands()[self.__action]

    ## Add command line arguments:
    def set_cli_parser_args (self, parser, *args, **kwargs):
        parser.add_argument ('action', choices=self.get_cli_commands().keys(), )
        parser.add_argument ('-v', '--debug', choices=['d', 'debug', 'i', 'info', 'w', 'warning', 'e', 'error',], default='info',)
        pass

    ## Returns command line arguments parser:
    def get_cli_parser (self, *args, **kwargs):
        return argparse.ArgumentParser(*args, **kwargs)

    ## Returns namespase of parsed command line:
    def cli_parse_argv (self, argv, *args, **kwargs):
        parser = self.get_cli_parser()
        self.set_cli_parser_args(parser)
        return parser.parse_args(argv)

    ## Process command line arguments by namespace:
    def cli_process_args(self, namespace, *args, **kwargs):
        self.__action = namespace.action

    def __cli_process_args(self, namespace, *args, **kwargs):
        logging_kwargs = {
            'format' : self.__format,
            'datefmt': self.__datefmt,
        }
        
        if namespace.debug in ('d', 'debug'):
            logging_kwargs['level'] = logging.DEBUG
        elif namespace.debug in ('i', 'info'):
            logging_kwargs['level'] = logging.INFO
        elif namespace.debug in ('w', 'warn', 'warning'):
            logging_kwargs['level'] = logging.WARNING
        elif namespace.debug in ('e', 'err', 'error'):
            logging_kwargs['level'] = logging.ERROR

        logging.basicConfig(**logging_kwargs)
        self.cli_process_args(namespace)




    def cli(self):
        namespace = self.cli_parse_argv(sys.argv[1:])
        self.__cli_process_args(namespace)

        self.run()


    def process_row(self, id, row):
        return row
