import os
from typing import Any, List, Sequence, Dict

import disnake
from disnake import Option, Message, Intents
from disnake.ext import commands
from disnake.ext.commands import slash_core, InvokableSlashCommand

import config


class BaseHook:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


class OnLoadHook(BaseHook):
    pass


class OnMessageHook(BaseHook):
    pass


class DorsDiscord(commands.Bot):
    def __init__(self, **options: Any):
        super().__init__(**options)

        self.plugins = {}
        self.message_hooks = []

        modules = []
        whitelistonly = False
        for module in os.listdir(os.path.dirname("modules/")):
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            module = module[:-3]
            modules.append(module)
            if module in config.whitelistonly_modules:
                whitelistonly = True

        self.slash_command()

        if whitelistonly:
            for module in config.whitelistonly_modules:
                self.load_module(module)
        else:
            for module in modules:
                if module in config.disabled_modules:
                    continue
                self.load_module(module)

    def load_module(self, module: str):
        print("Loading", module)
        themodule = __import__("modules." + module, locals(), globals())
        themodule = getattr(themodule, module)

        self.plugins[module] = themodule

        funcs = [f for _, f in themodule.__dict__.items() if callable(f)]
        for func in funcs:
            if isinstance(func, InvokableSlashCommand):
                self.add_slash_command(func)
            elif isinstance(func, OnLoadHook):
                func.func(self)
            elif isinstance(func, OnMessageHook):
                self.message_hooks.append(func)

    async def on_message(self, message: Message) -> None:
        print(f'> <{message.author}>: {message.content}')
        for func in self.message_hooks:
            await func.func(self, message)


slash_command = slash_core.slash_command

def on_load():
    def decorator(func):
        return OnLoadHook(func)

    return decorator


def on_message():
    def decorator(func):
        return OnMessageHook(func)

    return decorator
