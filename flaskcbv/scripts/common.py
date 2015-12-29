import logging
import sys, os
import string, random
import traceback

## Some helpfull definations:
class CommonMixin(object):

    ## Get file path, with existent checks:
    @staticmethod
    def get_file_path(file_, logprefix='CommonMixin: '):
        file_ = os.path.abspath(file_)
        logging.debug(logprefix + "got file: %s" % file_)

        try:
            fstat = os.stat(file_)
        except Exception as err:
            logging.error(logprefix + 'Error on opening file %s: %s' % (file_, err))
            raise(err)

            ## Not is file:
            if not stat.S_ISREG(fstat.st_mode):
                logging.error(logprefix + '%s IS NOT A FILE!' % file_)
                raise(Exception("Not a file!"))
        return file_


    ## Log as debug code traceback(can be used to fined exceptions):
    @staticmethod
    def log_traceback():
        data = traceback.format_exception(*sys.exc_info())
        data_ = ''.join(data) + '\n'
        logging.debug('%s===================' % data_)


    @staticmethod
    def token_gen(size=6):
        chars=string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))


    @classmethod
    def static_token(cls_, size=6):
        if hasattr(cls_, '__mytoken'):
            return getattr(cls_, '__mytoken')
        setattr(cls_, '__mytoken', cls_.token_gen(size=size))
        return cls_.static_token()

