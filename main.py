import asyncio
import os

from aiohttp import web
import discord
from discord.ext import commands


MY_GUILD = discord.Object(id=os.environ['GUILD_ID'])
TOKEN = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()


class MyBot(commands.Bot):
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


bot = MyBot('/', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


async def handler(request: web.BaseRequest):
    return web.Response(text='OK')


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    print('Serving on http://127.0.0.1:8000/')

    extensions = [f[:-3] for f in os.listdir('./commands') if f.endswith('.py')]
    async with bot:
        for extension in extensions:
            await bot.load_extension('commands.' + extension)
        await bot.start(TOKEN)


if __name__ == "__main__":
    discord.utils.setup_logging(root=False)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
