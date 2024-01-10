import enum
import io

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class Fonts(enum.Enum):
    ゴシック体 = 'notosans-mono-bold'
    極太ゴシック体 = 'mplus-1p-black'
    丸ゴシック体 = 'rounded-x-mplus-1p-black'
    明朝体 = 'ipamjm'
    毛筆 = 'aoyagireisyoshimo'
    英字 = 'LinLibertine_RBah'


@app_commands.command(name='emoji', description='絵文字を生成するよ!')
@app_commands.describe(text='絵文字にするテキスト',
                       red='赤の明度(0~255)', green='緑の明度(0~255)', blue='青の明度(0~255)',
                       font='テキストのフォント')
@app_commands.checks.cooldown(1, 10, key=None)
async def generate_emoji(interaction: discord.Interaction,
                         text: str,
                         red: int, green: int, blue: int,
                         font: Fonts):
    if min(red, green, blue) < 0 or max(red, green, blue) > 255:
        await interaction.response.send_message('色は0~255の範囲で指定してね!', ephemeral=True)
        return
    params = {
        'align': 'center',
        'back_color': '00000000',
        'color': '{:02x}{:02x}{:02x}ff'.format(red, green, blue),
        'font': font.value,
        'locale': 'ja',
        'public_fg': 'false',
        'size_fixed': 'false',
        'stretch': 'true',
        'text': text.replace('\\n', '\n')
             }

    async with aiohttp.ClientSession() as session:
        async with session.get('https://emoji-gen.ninja/emoji', params=params) as resp:
            if resp.status != 200:
                await interaction.response.send_message(f'生成に失敗したよ!: {resp.status}',
                                                        ephemeral=True)
                return
            data = io.BytesIO(await resp.read())
            await interaction.response.send_message(file=discord.File(data, f'{text}.png'))


async def setup(bot: commands.Bot):
    bot.tree.add_command(generate_emoji)
