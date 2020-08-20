from api import on_command


@on_command('test')
async def asdf(client, message, args):
    await message.channel.send('Test OK ' + str(args))
