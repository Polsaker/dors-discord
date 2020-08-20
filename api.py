def on_message(func):
    func._handler = 'on_message'
    return func


def on_raw_reaction_add(func):
    func._handler = 'on_raw_reaction_add'
    return func


def on_command(command, help=None):
    def wrap(func):
        func._handler = 'command'
        func._command = command
        func._help = help
        return func
    return wrap
