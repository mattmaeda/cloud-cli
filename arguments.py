import imp
import logging.config
import os
import sys

MY_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_INTERFACE_PATH = os.path.join(MY_PATH, "implementation")

logging.config.fileConfig(os.path.join(MY_PATH, 'logging.conf'))

class CLIArgument(object):
    def __init__(self, interface_name, custom_interface=None):

        self.interface = interface_name
        self.args = {}
        self.req_args = {}
        self.functions = {}
        self.interface_path = DEFAULT_INTERFACE_PATH

        if custom_interface is not None:
            logging.info("Loading custom interface " \
                         "directory {}".format(custom_interface))
            self.interface_path = custom_interface


    def init(self, interfaces, namespace, command):

        for i in interfaces:
            self.req_args[i] = []
            exists = None

            i_path = os.path.join(self.interface_path, i)
            n_path = os.path.join(i_path, namespace)
            c_path = os.path.join(n_path, command)

            if not os.path.exists(i_path):
                exists = False
                msg = "Missing interface {}".format(i)
                logging.warning(msg)

            elif not os.path.exists(n_path):
                exists = False
                msg = "Missing namespace {} for " \
                    "interface {}".format(namespace, i)
                logging.warning(msg)

            elif not os.path.exists(c_path):
                exists = False
                msg = "Missing command {} on namespace " \
                    "{} for interface {}".format(command, namespace, i)
                logging.warning(msg)

            else:
                exists = True
                mod = imp.load_source('implementation', c_path)

                for a in getattr(mod, "ARGS"):
                    n = a.get("name")
                    r = a.get("required", False)
                    h = a.get("help", "Help not defined for {}".format(n))

                    self.args[n] = {
                        "name": "--{}".format(n),
                        "help": h
                    }

                    if r:
                        self.req_args[i].append({"name": n, "help": h})

                self.functions[i] = getattr(mod, "execute")

            if not exists:
                self.functions[i] = self.command_not_implemented


    def add_parser_args(self, parser):
        for k, v in self.args.iteritems():
            parser.add_argument(v.get("name"), dest=k, help=v.get("help"))

        parser.set_defaults(func=self.execute)


    def execute(self, parser, args):
        interface = getattr(args, self.interface)
        self.validate(parser, interface, args)
        return self.functions[interface](args)


    def validate(self, parser, interface, args):
        missing_values = []

        for a in self.req_args[interface]:
            if getattr(args, a.get("name")) is None:
                missing_values.append({
                    "name": a.get("name"),
                    "help": a.get("help")})


        if len(missing_values) > 0:
            parser.print_help()
            self.print_additional_usage(missing_values)
            sys.exit(1)


    def command_not_implemented(self, args):
        raise NotImplementedError("Command is not implemented")


    def print_additional_usage(self, required_args):
        fmt_usage = map(lambda a: "  --{}\t\t{}".format(a.get("name"),
                                                        a.get("help")),
                        required_args)

        print ""
        print "interface required arguments:"
        print "{}".format("\n".join(fmt_usage))
