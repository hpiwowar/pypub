import logging

__all__ = ["mylog"]

LOG_FILE_NAME = "info.log"

# Set up logging
# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s %(funcName)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOG_FILE_NAME,
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt="%H:%M:%S")
console.setFormatter(formatter)
# add the handler to the my logger
logging.getLogger('').addHandler(console)
mylog = logging.getLogger('')

