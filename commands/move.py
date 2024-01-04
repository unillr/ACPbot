import discord
from discord import app_commands
from discord.ext import commands


class MemberSelectMenu(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction):
        self.move_from = interaction.user.voice.channel
        self.move_to = interaction.channel
        options = [discord.SelectOption(label=m.display_name, value=str(m.id))
                   for m in self.move_from.members]
        super().__init__(placeholder='移動させるメンバーを選択…',
                         max_values=len(options),
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        error = None
        members = [interaction.guild.get_member(int(id)) for id in self.values]
        for member in members:
            try:
                await member.move_to(self.move_to)
            except (discord.Forbidden, discord.HTTPException) as e:
                error = e
        if error is None:
            await interaction.edit_original_response(content='VCを移動したよ!', view=None)
        else:
            await interaction.edit_original_response(content='移動に失敗したよ!', view=None)
            raise error


class EveryoneButton(discord.ui.Button):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(style=discord.ButtonStyle.primary, label='全員')
        self.move_from = interaction.user.voice.channel
        self.move_to = interaction.channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        error = None
        for member in self.move_from.members:
            try:
                await member.move_to(self.move_to)
            except (discord.Forbidden, discord.HTTPException) as e:
                error = e
        if error is None:
            await interaction.edit_original_response(content='VCを移動したよ!', view=None)
        else:
            await interaction.edit_original_response(content='移動に失敗したよ!', view=None)
            raise error


class MemberSelectMenuView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.add_item(MemberSelectMenu(interaction))
        self.add_item(EveryoneButton(interaction))


@app_commands.command(description='まとめてVCを移動できるよ!')
@app_commands.checks.bot_has_permissions(move_members=True)
async def move(interaction: discord.Interaction):
    if (isinstance(interaction.channel, discord.VoiceChannel)
            and interaction.user.voice is not None):
        await interaction.response.send_message(
            view=MemberSelectMenuView(interaction),
            ephemeral=True)
    else:
        await interaction.response.send_message(
            content='VCに入っていないまたはボイスチャンネルじゃないよ!',
            ephemeral=True)


async def setup(bot: commands.Bot):
    bot.tree.add_command(move)
