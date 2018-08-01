#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, logging, subprocess, coloredlogs, verboselogs

def run(command, chdir, action, silent=True, shell=True):
    errors = 0
    logger = logging.getLogger(__name__)
    logger.debug('\nRunning %s' % action)

    logger.debug('    %s' % command)
    process = subprocess.Popen(
        command,
        cwd=chdir,
        shell=True,
        bufsize=0,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output = ''
    output, _ = process.communicate()

    if not silent:
        logger.notice(output.decode('utf-8'))

    if process.returncode == 0:
        logger.success('    %s OK' % action)
    else:
        if type(output) is bytes:
            output = output.decode("utf-8", "replace")
        logger.warn('\n'.join(output.splitlines()))
        logger.critical('    %s FAILED' % action)
        errors += 1
    return errors


if __name__ == '__main__':
    FORMAT = '%(message)s'
    verboselogs.install()
    logger = logging.getLogger(__name__)
    os.environ['COLOREDLOGS_LOG_FORMAT'] = FORMAT
    coloredlogs.install(level='DEBUG', logger=logger)
    
    chdir = sys.argv[1]
    errors = 0
    errors += run(
        command='pip install -e .[ci]',
        chdir="%s/sentinel" % chdir,
        action='Install require for tests'
    )
    errors += run(
        command='coverage run -m unittest',
        chdir="%s/sentinel" % chdir,
        action="Unit tests",
        silent=False
    )
    errors += run(
        command='coverage report -m',
        chdir="%s/sentinel" % chdir,
        action="Coverage report",
        silent=False
    )
    errors += run(
        command='flake8 --ignore=E501 .',
        chdir='%s/sentinel' % chdir,
        action="Code sniffer"
    )
    errors += run(
        command='pylint --ignore=tests -r y sentinel',
        chdir=chdir,
        action="Python linter",
        silent=False
    )
    errors += run(
        command="radon mi -i tests -s sentinel",
        chdir=chdir,
        action="Verify project maintainability",
        silent=False
    )
    errors += run(
        command="xenon --max-absolute B --max-modules A --max-average A sentinel",
        chdir=chdir,
        action="Verify project cyclomatic complexity",
        silent=False
    )

    sys.exit(0 if not errors else 1)
