import enum

import discord
from discord import app_commands
from discord.ext import commands


class Hands(enum.Enum):
    グー = '✊'
    チョキ = '✌️'
    パー = '🖐️'


class JankenView(discord.ui.View):
    def __init__(self, user: discord.Member, hand: Hands):
        self.user = user
        self.hand = hand
        super().__init__()

    @discord.ui.select(
        placeholder='出す手を選択…',
        options=[discord.SelectOption(label=h.name, value=h.value, emoji=h.value) for h in Hands])
    async def display_result(self, interaction: discord.Interaction, select: discord.ui.Select):
        hand1 = self.hand.value
        hand2 = select.values[0]
        content = f'{self.user.mention}{hand1} vs. {hand2}{interaction.user.mention}\n'
        if hand1 == hand2:
            content += '引き分け!'
        elif ((hand1 == '✊' and hand2 == '✌️') or
              (hand1 == '✌️' and hand2 == '🖐️') or
              (hand1 == '🖐️' and hand2 == '✊')):
            content += f'{self.user.mention}の勝ち!'
        else:
            content += f'{interaction.user.mention}の勝ち!'

        await interaction.response.edit_message(content=content, view=None)


@app_commands.command(description='じゃんけんができるよ!')
@app_commands.describe(hand='出す手')
async def janken(interaction: discord.Interaction, hand: Hands):
    user = interaction.user
    await interaction.response.send_message(view=JankenView(user, hand))


async def setup(bot: commands.Bot):
    bot.tree.add_command(janken)
