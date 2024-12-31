import random

import discord
from discord import app_commands
from discord.ext import commands


@app_commands.command(name='omikuji', description='おみくじが引けるよ!')
async def omikuji(interaction: discord.Interaction):
    fortunes = ['大吉', '吉', '中吉', '小吉', '末吉', '凶', '大凶']
    weights = [3, 4, 5, 4, 3, 2, 1]
    fortune = random.choices(fortunes, weights)[0]
    await interaction.response.send_message(fortune)


async def setup(bot: commands.Bot):
    bot.tree.add_command(omikuji)
