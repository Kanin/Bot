import os
import subprocess

import discord
from discord.ext import commands

from utils.checks import checks
from utils.functions import pagify


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="List all modules on the bot")
    async def modules(self, ctx):
        cog_list, cogs_loaded, cogs_unloaded = [], "```diff\n+\t", ""
        event_list, events_loaded, events_unloaded = [], "```diff\n+\t", ""
        cogs, events = [], []
        bot_cogs = {}
        em = discord.Embed(color=self.bot.color)
        em.set_author(name="Bot modules:")
        em.set_thumbnail(url=self.bot.user.avatar_url)
        paths = ["modules/Commands", "modules/Events"]
        for path in paths:
            for file in os.listdir(path):
                if not file.endswith(".py"):
                    pass
                else:
                    if path == paths[0]:
                        cog_list.append(file[:-3])
                    else:
                        event_list.append(file[:-3])
        for name, obj in self.bot.cogs.items():
            if "modules.Cogs" in str(obj):
                cogs.append(name)
            else:
                events.append(name)
        bot_cogs["cogs"] = cogs
        bot_cogs["events"] = events
        for k, v in bot_cogs.items():
            if k == "cogs":
                for cog in v:
                    if cog in cog_list:
                        cog_list.remove(cog)
            else:
                for event in v:
                    if event in event_list:
                        event_list.remove(event)
        cogs_loaded += ", ".join(bot_cogs["cogs"])
        cogs_unloaded += ", ".join(cog_list)
        events_loaded += ", ".join(bot_cogs["events"])
        events_unloaded += ", ".join(event_list)
        cogs_loaded += f"\n-\t{cogs_unloaded}```" if cogs_unloaded else "```"
        events_loaded += f"\n-\t{events_unloaded}```" if events_unloaded else "```"
        em.add_field(name="Cogs:", value=cogs_loaded)
        em.add_field(name="Events:", value=events_loaded)
        await ctx.send(embed=em)

    @checks.is_owner()
    @commands.group(hidden=True, case_insensitive=True, description="Load a module")
    async def load(self, ctx):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @load.command(name="cog", aliases=["c"], description="Load a cog")
    async def load_cog(self, ctx, cog_name: str):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        cog_name = cog_name.replace(".py", "")
        try:
            self.bot.load_extension(f"modules.Commands.{cog_name}")
        except commands.ExtensionAlreadyLoaded:
            return await ctx.send_error(f"Cog {cog_name} is already loaded!")
        except commands.ExtensionNotFound:
            return await ctx.send_error(f"Cog {cog_name} could not be found!")
        await ctx.send(f"Cog {cog_name} has now been loaded!")

    @load.command(name="event", aliases=["e"], description="Load an event")
    async def load_event(self, ctx, event_name: str):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        event_name = event_name.replace(".py", "")
        try:
            self.bot.load_extension(f"modules.Events.{event_name}")
        except commands.ExtensionAlreadyLoaded:
            return await ctx.send_error(f"Event {event_name} is already loaded!")
        except commands.ExtensionNotFound:
            return await ctx.send_error(f"Event {event_name} could not be found!")
        await ctx.send(f"Event {event_name} has now been loaded!")

    @checks.is_owner()
    @commands.group(hidden=True, case_insensitive=True, description="Unload a module")
    async def unload(self, ctx):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @unload.command(name="cog", aliases=["c"], description="Unload a cog")
    async def unload_cog(self, ctx, cog_name: str):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        cog_name = cog_name.replace(".py", "")
        try:
            self.bot.unload_extension(f"modules.Cogs.{cog_name}")
        except commands.ExtensionNotLoaded:
            return await ctx.send_error(f"Cog {cog_name} is not loaded!")
        except commands.ExtensionNotFound:
            return await ctx.send_error(f"Cog {cog_name} could not be found!")
        await ctx.send(f"Cog {cog_name} is now unloaded!")

    @unload.command(name="event", aliases=["e"], description="Unload an event")
    async def unload_event(self, ctx, event_name: str):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        event_name = event_name.replace(".py", "")
        try:
            self.bot.unload_extension(f"modules.Events.{event_name}")
        except commands.ExtensionNotLoaded:
            return await ctx.send_error(f"Event {event_name} is not loaded!")
        except commands.ExtensionNotFound:
            return await ctx.send_error(f"Event {event_name} could not be found!")
        await ctx.send(f"Event {event_name} is now unloaded!")

    @checks.is_owner()
    @commands.group(hidden=True, case_insensitive=True, description="Reload a module")
    async def reload(self, ctx):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @reload.command(name="cog", aliases=["c"], description="Reload a cog")
    async def reload_cog(self, ctx, cog_name: str):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        cog_name = cog_name.replace(".py", "")
        try:
            self.bot.reload_extension(f"modules.Commands.{cog_name}")
        except commands.ExtensionNotLoaded:
            return await ctx.send_error(f"Cog {cog_name} is not loaded!")
        except commands.ExtensionNotFound:
            return await ctx.send_error(f"Cog {cog_name} could not be found!")
        await ctx.send(f"Cog {cog_name} has been reloaded!")

    @reload.command(name="event", aliases=["e"], description="Reload an event")
    async def reload_event(self, ctx, event_name: str):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        event_name = event_name.replace(".py", "")
        try:
            self.bot.reload_extension(f"modules.Events.{event_name}")
        except commands.ExtensionNotLoaded:
            return await ctx.send_error(f"Event {event_name} is not loaded!")
        except commands.ExtensionNotFound:
            return await ctx.send_error(f"Event {event_name} could not be found!")
        await ctx.send(f"Event {event_name} has been reloaded!")

    @checks.is_owner()
    @commands.command(hidden=True, description="Pull updates from git")
    async def pull(self, ctx):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        paged = pagify(
            subprocess.Popen(
                ["git", "pull"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            ).stdout.read().decode()
        )
        for page in paged:
            p = f"```css\n{page}```"
            await ctx.send(p)

    @checks.is_owner()
    @commands.command(name="raise", hidden=True, description="Raise a test exception")
    async def _raise(self, ctx):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        await ctx.send("Raising a test exception..")
        raise Exception(f"Exception raised by {ctx.author}")

    @checks.is_owner()
    @commands.command(hidden=True, description="Force a user to run a command")
    async def sudo(self, ctx, user: discord.Member, *, command):
        """{"permissions": {"user": ["bot_owner"], "bot": []}}"""
        message = ctx.message
        prefix = await self.bot.get_prefix(message)
        message.author = user
        message.content = prefix + command
        await self.bot.invoke(await self.bot.get_context(message))


def setup(bot):
    bot.add_cog(Core(bot))
