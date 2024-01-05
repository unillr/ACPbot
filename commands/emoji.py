import enum
import io

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from yarl import URL


class Fonts(enum.Enum):
    ゴシック体 = 'notosans-mono-bold'
    極太ゴシック体 = 'mplus-1p-black'
    丸ゴシック体 = 'rounded-x-mplus-1p-black'
    明朝体 = 'ipamjm'
    毛筆 = 'aoyagireisyoshimo'
    英字 = 'LinLibertine_RBah'


@app_commands.command(name='emoji')
@app_commands.checks.has_permissions(manage_expressions=True)
async def generate_emoji(interaction: discord.Interaction,
                         text: str,
                         color: str,
                         font: Fonts):
    url = URL('https://emoji-gen.ninja/emoji')
    query = {
        'align': 'center',
        'back_color': '00000000',
        'color': color + 'ff',
        'font': font.value,
        'locale': 'ja',
        'public_fg': str(False),
        'size_fixed': str(False),
        'stretch': str(True),
        'text': text.replace('\\n', '\n')
             }
    url_with_query = url.with_query(query)

    async with aiohttp.ClientSession() as session:
        async with session.get(url_with_query) as resp:
            if resp.status != 200:
                await interaction.response.send_message(f'生成に失敗したよ!: {resp.status}',
                                                        ephemeral=True)
                return
            data = io.BytesIO(await resp.read())
            await interaction.response.send_message(file=discord.File(data, f'{text}.png'))


async def setup(bot: commands.Bot):
    bot.tree.add_command(generate_emoji)
