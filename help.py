import discord
from discord.ext import commands


class HelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return "{0.clean_prefix}{1.qualified_name}".format(self, command)

    async def send_bot_help(self, mapping):
        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds)
            command_signatures = ["`{}` {}".format(self.get_command_signature(c), "- {}".format(c.brief) if c.brief else "") for c in filtered]
            if command_signatures:
                unique_signatures = list()
                for c in command_signatures:
                    if c not in unique_signatures:
                        unique_signatures.append(c)
                channel = self.get_destination()
                intro_str = "Here are my valid commands!\n\t"
                outro_str = "\nUse `fk!help <command>` to get more info.\n\nEden created by kavron#8663."
                commands_str = "\n\t".join(unique_signatures)
                await channel.send("{}{}{}".format(intro_str, commands_str, outro_str))
        return

    async def send_command_help(self, command):
        if command.description:
            header = "**{}**".format(command.description)
        else:
            header = "**{}**".format(command.name)

        if command.usage:
            usage = "Usage: `{} {}`".format(self.get_command_signature(command), command.usage)
        else:
            usage = "Usage: `{}`".format(self.get_command_signature(command))

        helptext = command.help

        aliases = None
        if len(command.aliases) > 0:
            aliases = "Aliases: `" + "`, `".join(command.aliases) + "`"

        if aliases:
            out_str = "{}\n\n{}\n{}\n\n{}".format(header, usage, aliases, helptext)
        else:
            out_str = "{}\n\n{}\n\n{}".format(header, usage, helptext)
        await self.get_destination().send(out_str)
        return
