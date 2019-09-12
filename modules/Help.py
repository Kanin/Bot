from discord.ext import commands as dcommands
import discord
import json


class MyHelpCommand(dcommands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            em = discord.Embed(description=page, color=11533055)
            em.set_author(name="Here is the help you requested!")
            await destination.send(embed=em)

    def get_opening_note(self):
        return None

    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    def get_ending_note(self):
        command_name = self.context.invoked_with
        return f"Type `{self.clean_prefix}{command_name} [command]` for more info on a command.\n" \
               f"You can also type `{self.clean_prefix}{command_name} [category]` for more info on a category."

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = ", ".join(c.name for c in commands) + "\n"
            self.paginator.add_line(f"__**{heading}**__")
            self.paginator.add_line(joined)

    def add_subcommand_formatting(self, command):
        fmt = f"{self.clean_prefix}{command.qualified_name} - `{command.description}`"\
            if command.description else\
              f"{self.clean_prefix}{command.qualified_name}"
        self.paginator.add_line(fmt)

    def add_aliases_formatting(self, aliases):
        self.paginator.add_line(self.aliases_heading + ', '.join(aliases), empty=True)

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:
            try:
                docs = json.loads(command.help)
                permissions = self.generate_perm_docs(docs["permissions"])
                line = "```ml\n"
                line += f"{permissions}"
                line += "\n```"
                self.paginator.add_line(line, empty=False)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()
            except Exception as e:
                print(e)

    def generate_perm_docs(self, docs):
        ctx = self.context
        user, guild, channel = ctx.author, ctx.guild, ctx.channel
        user_needs_perms = docs["user"] + ["send_messages"]
        bot_needs_perms = docs["bot"] + user_needs_perms
        user_perms = [x[0] for x in iter(channel.permissions_for(user)) if x[1]]
        bot_perms = [x[0] for x in iter(channel.permissions_for(guild.me)) if x[1]]
        user_perms_list = ", ".join([x.replace("_", " ").title() for x in user_needs_perms if x in user_perms])
        user_has_perms = "\"" + user_perms_list + "\"" if user_perms_list else "User missing all required permissions"

        user_no_perms = ", ".join([x.replace("_", " ").title() for x in user_needs_perms if x not in user_perms])
        user_no_perms = "'" + user_no_perms + "'" if user_no_perms else "User has all required permissions"

        bot_perms_list = ", ".join([x.replace("_", " ").title() for x in bot_needs_perms if x in bot_perms])
        bot_has_perms = "\"" + bot_perms_list + "\"" if bot_perms_list else "Bot missing all required permissions"

        bot_no_perms = ", ".join([x.replace("_", " ").title() for x in bot_needs_perms if x not in bot_perms])
        bot_no_perms = "'" + bot_no_perms + "'" if bot_no_perms else "Bot has all required permissions"
        msg = f"Permissions:\n"
        msg += f"Bot:\n"
        msg += f"{bot_has_perms}\n"
        msg += f"{bot_no_perms}\n\n"
        msg += f"User:\n"
        msg += f"{user_has_perms}\n"
        msg += f"{user_no_perms}\n"
        return msg


class Help(dcommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand(aliases_heading="**Aliases:** ")
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
