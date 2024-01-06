import discord
from discord import app_commands
from discord.ext import commands


class InputNameModal(discord.ui.Modal):
    def __init__(self, attachment: discord.Attachment):
        self.attachment = attachment
        super().__init__(title='絵文字の名前を入力')

    name = discord.ui.TextInput(label='名前', min_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            image = await self.attachment.read()
            emoji = await interaction.guild.create_custom_emoji(name=self.name.value, image=image)
        except discord.HTTPException:
            await interaction.response.send_message('絵文字の追加に失敗したよ!', ephemeral=True)
            raise
        else:
            await interaction.response.send_message(f'絵文字を追加したよ! {emoji}')


@app_commands.context_menu(name='絵文字としてサーバーに追加')
@app_commands.checks.has_permissions(manage_expressions=True)
@app_commands.checks.bot_has_permissions(manage_expressions=True)
async def add_emoji(interaction: discord.Interaction, message: discord.Message):
    attachments = message.attachments
    if attachments and attachments[0].filename.endswith(('.jpg', '.png', '.gif')):
        await interaction.response.send_modal(InputNameModal(attachments[0]))
    else:
        await interaction.response.send_message('画像がないか対応していないよ!', ephemeral=True)


async def setup(bot: commands.Bot):
    bot.tree.add_command(add_emoji)
