"""
Class contains the CLI argument implementation details
"""
import imp
import logging.config
import os
import sys

MY_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_IMPLEMENTATION_PATH = os.path.join(MY_PATH, "implementation")

logging.config.fileConfig(os.path.join(MY_PATH, 'logging.conf'))

class CLIArgument(object):
    """ Class contains the actual CLI argument implementation details
    """
    def __init__(self, cli_prog_name, implementation_options,
                 cli_argument_namespace, cli_argument_name,
                 custom_interface=None):

        self.cli_prog_name = cli_prog_name
        self.implementation_options = implementation_options
        self.cli_argument_namespace = cli_argument_namespace
        self.cli_argument_name = cli_argument_name
        self.cli_arguments = {}
        self.required_cli_arguments = {}
        self.cli_functions = {}
        self.implementation_path = DEFAULT_IMPLEMENTATION_PATH

        if custom_interface is not None:
            logging.info("Loading custom interface " \
                         "directory {}".format(custom_interface))
            self.implementation_path = custom_interface

        self.load_implementation_options()


    def load_implementation_options(self):
        """ Iterates through the various implementation options
            and loads the implementation to the CLI parser
        """
        for namespace_option in self.implementation_options:
            if namespace_option not in self.required_cli_arguments:
                self.required_cli_arguments[namespace_option] = []

            self.setup_implementation(namespace_option)


    def setup_implementation(self, namespace_option):
        """ Checks the implementation setting and then loads it
            if it is implemented
        """
        namespace_command_path = os.path.join(self.implementation_path,
                                              namespace_option,
                                              self.cli_argument_namespace,
                                              self.cli_argument_name)

        namespace_python_module = "{}.py".format(namespace_command_path)

        if not os.path.exists(namespace_python_module):
            msg = "Missing command {} on namespace {} for " \
                  "implementation {} at {}".format(self.cli_argument_name,
                                                   self.cli_argument_namespace,
                                                   namespace_option,
                                                   namespace_command_path)
            logging.warning(msg)
            self.cli_functions[namespace_option] = self.command_not_implemented

        else:
            self.load_command_implementation(namespace_option,
                                             namespace_python_module)


    def command_not_implemented(self, user_entered_cli_args):
        """ This function is called when the command is not implemented """
        raise NotImplementedError("Command is not implemented")


    def load_command_implementation(self, namespace_option,
                                    namespace_python_module):
        """ Loads the implementation of the command for the given
            namespace and its corresponding function call
        """
        module = imp.load_source('implementation', namespace_python_module)
        self.load_implementation_arguments(namespace_option,
                                           getattr(module, "ARGS"))
        self.cli_functions[namespace_option] = getattr(module, "execute")


    def load_implementation_arguments(self, namespace_option,
                                      module_arguments):
        """ Loads the implementation arguments for the command """
        for implementation_argument in module_arguments:
            arg_name = implementation_argument.get("name")
            required = implementation_argument.get("required", False)
            help_text = implementation_argument.get("help",
                                                    "Help not defined")

            self.cli_arguments[arg_name] = {
                "name": "--{}".format(arg_name),
                "help": help_text
            }

            if required:
                req_arg = {"name": arg_name, "help": help_text}
                self.required_cli_arguments[namespace_option].append(req_arg)


    def attach_arguments_to_parser(self, parser):
        """ Accepts a parser and attaches the implemented arguments
            and execute function
        """
        for destination, argument in self.cli_arguments.iteritems():
            parser.add_argument(argument.get("name"),
                                dest=destination,
                                help=argument.get("help"))

        parser.set_defaults(func=self.execute)


    def execute(self, parser, user_entered_args):
        """ Validates the user entered args and if valid
            executes the attached implemented function
        """
        impl = getattr(user_entered_args, self.cli_prog_name)
        self.validate(parser, impl, user_entered_args)
        return self.cli_functions[impl](user_entered_args)


    def validate(self, parser, implementation, args):
        """ Validates that any required argument is present
        """
        valid = True
        missing_values = []

        for arg in self.required_cli_arguments[implementation]:
            if getattr(args, arg.get("name")) is None:
                valid = False
                missing_values.append({
                    "name": arg.get("name"),
                    "help": arg.get("help")})

        if not valid:
            parser.print_help()
            self.print_additional_usage(missing_values)
            sys.exit(1)


    def print_additional_usage(self, required_args):
        """ Prints the additional required implementation arguments
        """
        fmt_usage = ["--{}\t\t{}".format(a.get("name"), a.get("help"))
                     for a in required_args]

        print ""
        print "interface required arguments:"
        print "{}".format("\n".join(fmt_usage))
