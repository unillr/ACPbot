import json
import random

import discord
from discord import app_commands
from discord.ext import commands


class MapSelectMenu(discord.ui.Select):
    def __init__(self):
        with open('./images/maps/maps.json', 'r', encoding='utf-8') as f:
            self.maps = json.load(f)
        options = [discord.SelectOption(label=m) for m in self.maps.keys()]

        super().__init__(placeholder='除外するマップを選択…',
                         min_values=0,
                         max_values=len(options) - 1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        candicates = [m for m in self.maps.keys() if m not in self.values]
        map_name = random.choice(candicates)
        map_image = self.maps[map_name]

        embed = discord.Embed(title=map_name)
        embed.set_image(url=f'attachment://{map_image}')
        embed.set_footer(text='BAN: ' + (' / '.join(self.values) or 'なし'))

        attachments = [discord.File(f'./images/maps/{map_image}')]

        await interaction.response.edit_message(embed=embed, attachments=attachments, view=None)


class MapSelectMenuView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MapSelectMenu())


@app_commands.command(name='map', description='ランダムにマップを選択')
async def random_map(interaction: discord.Interaction):
    await interaction.response.send_message(view=MapSelectMenuView())


async def setup(bot: commands.Bot):
    bot.tree.add_command(random_map)
