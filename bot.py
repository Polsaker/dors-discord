#!/usr/bin/env python3
import os
from typing import Any, Callable

import discord
import yaml


class CoBot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.modules = {}
        self.handlers = {
            'on_message': [],
            'on_raw_reaction_add': []
        }

        self.commands = {}

        # Load config
        self.config = yaml.safe_load(open("config.yaml"))

        # Load modules
        for module in os.listdir(os.path.dirname("modules/")):
            if module == '__init__.py' or module[-3:] != '.py':
                continue

            module = module[:-3]
            if module in self.config['modules']['blacklist']:
                continue
            self.load_module(module)

    def load_module(self, module):
        print("Loading", module)
        themodule = __import__("modules." + module, locals(), globals())
        themodule = getattr(themodule, module)

        self.modules[module] = themodule

        # Iterate over all the methods in the module to find handlers
        funcs = [f for _, f in themodule.__dict__.items() if callable(f)]

        for func in funcs:
            func: object
            try:
                func._handler
            except AttributeError:
                continue
            if func._handler == 'command':
                self.commands[func._command] = func
            elif func._handler == 'on_message':
                self.handlers['on_message'].append(func)
            elif func._handler == 'on_raw_reaction_add':
                self.handlers['on_raw_reaction_add'].append(func)

    def run(self, *args, **kwargs):
        super().run(self.config['token'])

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        # comandos
        if message.content.strip().startswith(self.config['prefix']):
            command = message.content.strip().split()[0].replace(self.config['prefix'], '', 1)
            args = message.content.strip().split()[1:]

            if command in self.commands:
                try:
                    await self.commands[command](self, message, args)
                except Exception as e:
                    print('ERROR', e)

        for handler in self.handlers['on_message']:
            await handler(self, message)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member == self.user:
            return
        for handler in self.handlers['on_raw_reaction_add']:
            await handler(self, payload)


bot = CoBot()
bot.run()