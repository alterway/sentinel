"""Main module to listen events, get services and register them in backend"""
import sys
import argparse
from discovery.layers.presentation.coordination import registry
from discovery.layers.domain.utils.logger import set_logging

DEFAULT_LOG_LEVEL = 'info'


def main():
    parser = argparse.ArgumentParser(description='All Commands help')
    parser.add_argument('-l', '--log-level', type=str, default=DEFAULT_LOG_LEVEL, help='Log level', )
    subparsers = parser.add_subparsers(help='sub-command help')

    # add subparser of discovery command
    for name, command in registry.items():
        command.options(subparsers)

    # get all args
    args = parser.parse_args()

    # we set logger strategy.
    logger = set_logging(args.log_level.upper())

    args.func(args, logger)


if __name__ == '__main__':
    sys.exit(main())
