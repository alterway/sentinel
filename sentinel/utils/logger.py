import logging
import sys
import os


def set_logging():
    logger = logging.getLogger('STDOUT')
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(out_hdlr)
    logger.setLevel(logging.INFO if os.environ.get('DEBUG') is None else logging.DEBUG)
