"""
Class builds the CLI object
"""
import argparse
import logging.config
import os
import yaml
from arguments import CLIArgument

MY_PATH = os.path.abspath(os.path.dirname(__file__))

logging.config.fileConfig(os.path.join(MY_PATH, 'logging.conf'))


class CLI(object):
    """ Contains the primary CLI builder function that serves as the entry point
        for the CLI framework
    """

    def __init__(self, cli_config_file):
        config = self.load_cli_config_file(cli_config_file)

        self.cli = argparse.ArgumentParser(
            prog=config.get("entry").get("name"))

        cli_implementations = config.get("implementations")
        self.cli_implementation_name = cli_implementations.get("name")
        self.cli_implementation_options = cli_implementations.get("options")

        self.set_implementation_cli_name(cli_implementations.get("help"))
        self.set_cli_subparser_arguments(config.get("arguments"))


    def load_cli_config_file(self, cli_config_file):
        """ Loads the YAML config file for CLI """
        config = None

        logging.info(
            "Opening configuration file at {}".format(cli_config_file))
        with open(cli_config_file, "r") as handle:
            config = yaml.load(handle)

        return config


    def set_implementation_cli_name(self, implementation_help_text):
        """ Sets the CLI PROG name """
        self.cli.add_argument(self.cli_implementation_name,
                              help=implementation_help_text,
                              choices=self.cli_implementation_options)


    def set_cli_subparser_arguments(self, cli_argument_settings):
        """ Sets up the subparser for the CLI """
        subparser = self.cli.add_subparsers(help="Additional arguments")

        for cli_argument_setting in cli_argument_settings:
            cli_namespace_option = cli_argument_setting.get("name")
            parser = subparser.add_parser(cli_namespace_option,
                                          help=cli_argument_setting.get("help"))

            self.set_cli_parser(parser, cli_namespace_option,
                                cli_argument_setting.get("options"))


    def set_cli_parser(self, cli_parser, cli_namespace_option, cli_parser_options):
        """ Sets up the individual subparser parsers for CLI """
        help_text = "{} options".format(cli_namespace_option)
        cli_subparser = cli_parser.add_subparsers(help=help_text)

        for cli_argument_option_name in cli_parser_options:
            optional_argument_parser = cli_subparser.add_parser(cli_argument_option_name)

            # This sets the actual parser option implementation to the CLI
            self.set_cli_parser_option(optional_argument_parser,
                                       cli_namespace_option, cli_argument_option_name)


    def set_cli_parser_option(self, optional_argument_parser,
                              cli_namespace_option, cli_argument_option_name):
        """ Sets the parser option implmentation """
        cli_arg_implementation = CLIArgument(self.cli_implementation_name,
                                             self.cli_implementation_options,
                                             cli_namespace_option,
                                             cli_argument_option_name)

        cli_arg_implementation.attach_arguments_to_parser(optional_argument_parser)


    def run(self):
        """ Parses arguments and passes arguments to mapped function """
        args = self.cli.parse_args()
        args.func(self.cli, args)
