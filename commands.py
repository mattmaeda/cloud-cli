class CLICommand(object):

    def __init__(self, name, required, help_text):
        self.name = name
        self.required = required
