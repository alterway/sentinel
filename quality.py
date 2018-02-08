#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import sys
import logging


def add_coloring_to_emit_ansi(fn):

    def new(*args):
        levelno = args[1].levelno
        if levelno == 100:
            color = '\x1b[36m'
        elif levelno >= 50:
            color = '\x1b[31m'
        elif levelno >= 40:
            color = '\x1b[31m'
        elif levelno >= 30:
            color = '\x1b[33m'
        elif levelno >= 20:
            color = '\x1b[32m'
        elif levelno >= 10:
            color = '\x1b[90m'
        else:
            color = '\x1b[0m'
        args[1].msg = color + str(args[1].msg) + '\x1b[0m'

        return fn(*args)
    return new


def run(command, chdir, action, silent=True, shell=True):
    errors = 0
    logging.info('\nRunning %s' % action)

    logging.info('    %s' % command)
    process = subprocess.Popen(
        command,
        cwd=chdir,
        shell=True,
        bufsize=0,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if not silent:
        output = ''

        while True:
            char = process.stdout.read(1)

            if type(char) is bytes:
                char = char.decode("utf-8", "replace")

            if char == '' and process.poll() is not None:
                break
            if char != '':
                output += char

        logging.debug(output)
    else:
        output, error = process.communicate()

    if process.returncode == 0:
        logging.info('    %s OK' % action)
    else:
        if type(output) is bytes:
            output = output.decode("utf-8", "replace")
        logging.warn('\n'.join(output.splitlines()))
        logging.error('    %s FAILED' % action)
        errors += 1
    return errors


if __name__ == '__main__':
    FORMAT = '%(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

    errors = 0
    errors += run(command='pip install -e .', chdir='.', action='Install require')
    errors += run(command='pip install -e .[ci]', chdir='.', action='Install require for tests')
    errors += run(command='coverage run -m unittest', chdir='sentinel', action="Unit tests", silent=False)
    errors += run(command='coverage report --omit=/virtualenvs/*,testing/*,*tests*,utils/*,di.py,models.py,exceptions.py -m', chdir='sentinel', action="Coverage report", silent=False)
    errors += run(command='flake8 --ignore=E501 .', chdir='sentinel', action="Code sniffer")

    sys.exit(0 if errors == 0 else 1)
