from __future__ import annotations

from discord.abc    import GuildChannel
from discord        import (
    ApplicationContext,
    ChannelType,
    Cog,
    Colour,
    default_permissions,
    ForumChannel,
    Option,
    Permissions,
    SlashCommandGroup,
    SlashCommandOptionType,
    Thread
)
from typing     import TYPE_CHECKING

from ui         import *
from utilities  import *

if TYPE_CHECKING:
    from classes.bot    import KinoKi
    from classes.guild  import GuildData
####################################################################################################
class Listeners(Cog):

    def __init__(self, bot: KinoKi):

        self.bot: KinoKi = bot

####################################################################################################
    @Cog.listener("on_thread_create")
    async def crosspost(self, thread: Thread) -> None:

        jobs_data = self.get_guild(thread.guild.id).job_postings

        if thread.parent not in jobs_data.source_channels:
            return

        if not thread.applied_tags:
            return

        role_list = []

        for tag in thread.applied_tags:
            for role in thread.guild.roles:
                if tag.name.lower() == role.name.lower():
                    role_list.append(role)
                    jobs_data.update_stats(role)

            for job_tag in jobs_data.tags:
                if job_tag.parent.name.lower() == tag.name.lower():
                    for i in job_tag.roles:
                        role_list.append(i)

        string_mentions = [r.mention for r in role_list]
        mention_string = " | ".join(string_mentions)
        thread_message = await thread.fetch_message(thread.id)

        summary = (
            f">>> **New Post in {thread.parent.mention}**\n"
            f"{thread.mention}\n"
            f"{mention_string}\n"
            f"{thread.jump_url}"
        )

        for channel in jobs_data.post_channels:
            await channel.send(summary)

        return

####################################################################################################
    @Cog.listener("on_guild_channel_delete")
    async def channel_delete(self, channel: GuildChannel) -> None:

        try:
            guild_data = self.get_guild(channel.guild.id)
        except:
            return

        if channel.type is ChannelType.forum or channel.type is ChannelType.text:
            guild_data.job_postings.yeet_channel(channel)  # type: ignore

####################################################################################################
    @Cog.listener("on_guild_channel_update")
    async def channel_edit(self, before: ForumChannel, after: ForumChannel) -> None:

        guild = self.get_guild(before.guild.id)

        if before.type is not ChannelType.forum:
            return

        for tag in before.available_tags:
            if tag.id not in [t.id for t in after.available_tags]:
                for i, t in enumerate(guild.job_postings.tags):
                    if t.parent.id == tag.id:
                        guild.job_postings.tags.pop(i)
                        break

####################################################################################################
    def get_guild(self, guild_id: int) -> GuildData:

        for guild in self.bot.k_guilds:
            if guild.parent.id == guild_id:
                return guild

####################################################################################################
def setup(bot: KinoKi) -> None:

    bot.add_cog(Listeners(bot))

####################################################################################################
