from arguments import CLIArgument

import argparse
import logging.config
import os
import yaml

MY_PATH = os.path.abspath(os.path.dirname(__file__))

logging.config.fileConfig(os.path.join(MY_PATH, 'logging.conf'))

class CLI(object):
    """ Contains the primary CLI builder function that serves as the entry point
        for the CLI framework
    """
    def __init__(self, cli_config_file):
        self.config = cli_config_file
        self.cli = None


    def init(self):
        """ Returns the argument parser object """
        cfg = None

        logging.info("Opening configuration file at {}".format(self.config))
        with open(self.config, "r") as fh:
            cfg = yaml.load(fh)

        self.cli = argparse.ArgumentParser(prog=cfg.get("entry").get("name"))

        i = cfg.get("interfaces")
        self.cli.add_argument(i.get("name"), help=i.get("help"),
                              choices=map(lambda a: a, i.get("options")))

        sp = self.cli.add_subparsers(help="Additional arguments")

        for a in cfg.get("arguments"):
            p = sp.add_parser(a.get("name"), help=a.get("help"))
            sub_p = p.add_subparsers(help="{} options".format(a.get("name")))

            for o in a.get("options"):
                opt = sub_p.add_parser(o)

                c = CLIArgument(i.get("name"))
                c.init(i.get("options"), a.get("name"), o)
                c.add_parser_args(opt)


    def run(self):
        args = self.cli.parse_args()
        args.func(self.cli, args)
