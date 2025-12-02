import discord
from discord import app_commands
from discord.ext import commands


class RecruitBoard(discord.Embed):
    def __init__(self,
                 number: int | None = None,
                 participants: list[str] = [],
                 standbys: list[str] = [],
                 canceled: list[str] = []):
        if number is not None:
            title = f'残り募集人数: {number - len(participants) + 1}'
        else:
            title = None
        super().__init__(title=title)

        fields = {'参加者': participants, '空き待ち': standbys, 'キャンセル': canceled}
        for n, v in fields.items():
            self.add_field(name=n, value='\n'.join(v) if v else 'なし')


class RecruitView(discord.ui.View):
    def __init__(self, number: int | None, recruiter: str):
        super().__init__(timeout=86400)
        self.number = number
        self.participants = [recruiter]
        self.standbys = []
        self.canceled = []
        self.watchers = []

    @discord.ui.button(style=discord.ButtonStyle.primary, label='参加')
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidate = interaction.user.mention
        if candidate in self.participants or candidate in self.standbys:
            await interaction.response.send_message('すでに参加しているよ!', ephemeral=True)
            return
        if candidate in self.canceled:
            self.canceled.remove(candidate)

        if self.number is None or self.number > len(self.participants) - 1:
            self.participants.append(candidate)
            for watcher in self.watchers:
                if watcher != interaction.user:
                    await watcher.send(f"あなたがWatchした募集に{candidate}が参加したよ！")
        else:
            self.standbys.append(candidate)

        board = RecruitBoard(self.number, self.participants,
                             self.standbys, self.canceled)
        await interaction.response.edit_message(embed=board)

    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Watch")
    async def watch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.watchers:
            self.watchers.append(interaction.user)
            await interaction.response.send_message('誰かが参加するとDMで通知するよ！', ephemeral=True)
        else:
            self.watchers.remove(interaction.user)
            await interaction.response.send_message('Watchを取り消したよ！', ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.secondary, label='キャンセル')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        canceler = interaction.user.mention
        if canceler in self.participants:
            self.participants.remove(canceler)
            if self.standbys:
                candidate = self.standbys.pop(0)
                self.participants.append(candidate)
        elif canceler in self.standbys:
            self.standbys.remove(canceler)
        else:
            await interaction.response.send_message('まだ参加していないよ!', ephemeral=True)
            return
        self.canceled.append(canceler)

        board = RecruitBoard(self.number, self.participants,
                             self.standbys, self.canceled)
        await interaction.response.edit_message(embed=board)

    @discord.ui.button(style=discord.ButtonStyle.danger, label='招集')
    async def convene(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.mention not in self.participants:
            await interaction.response.send_message('参加者以外は招集できないよ!', ephemeral=True)
            return
        if interaction.user.voice is not None and (vc := interaction.user.voice.channel) is not None:
            notify_member = self.participants.copy()
            for member in vc.members:
                if member.mention in self.participants:
                    notify_member.remove(member.mention)
            if notify_member:
                await vc.send(' '.join(notify_member))
            await interaction.response.send_message('通知を送ったよ！', ephemeral=True)
        else:
            await interaction.response.send_message(' '.join(self.participants))


@app_commands.command(name='bo', description='一緒に遊ぶ仲間を募集できるよ!')
@app_commands.describe(content='募集内容', number='募集人数')
async def recruit(interaction: discord.Interaction,
                  content: str,
                  number: int | None):
    if number is not None:
        content += f' @{number}'
    recruiter = interaction.user.mention
    await interaction.response.send_message(content=content,
                                            embed=RecruitBoard(
                                                number, [recruiter]),
                                            view=RecruitView(
                                                number, recruiter),
                                            allowed_mentions=discord.AllowedMentions.all())


async def setup(bot: commands.Bot):
    bot.tree.add_command(recruit)
