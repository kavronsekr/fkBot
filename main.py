import discord
from discord.ext import commands
from player_cache import PlayerCache
import os
import random
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

cache = PlayerCache()

token_filename = 'tokens.txt'
token_file = open(token_filename, 'r')
token = token_file.readline()

ping_strings = ['Pong!', ':heartpulse:',
                'Taco Baco!', ':eyes:',
                ':ping_pong:', 'bb!love',
                'Thomas Dracaena hit a ground out to Edric Tosser',
                'Have you fed your hexbugs today?',
                'Chorby Short! Chorby Tall! Chorby swings at every ball!']

hitting_stats = ['hittingRating',
                 'divinity', 'martyrdom',
                 'moxie', 'musclitude',
                 'patheticism', 'thwackability',
                 'tragicness']
pitching_stats = ['pitchingRating',
                  'coldness', 'overpowerment',
                  'ruthlessness', 'shakespearianism',
                  'suppression', 'unthwackability']
baserunning_stats = ['baserunningRating',
                     'baseThirst', 'continuation',
                     'groundFriction', 'indulgence',
                     'laserlikeness']
defense_stats = ['defenseRating',
                 'anticapitalism', 'chasiness',
                 'omniscience', 'tenaciousness',
                 'watchfulness']
vibe_stats = ['buoyancy', 'cinnamon', 'pressurization']
other_stats = ['totalFingers', 'peanutAllergy',
               'soul']

default_settings = {"prefix": "fk!",
                    "channels": [],
                    "roles": []
                    }
settings = dict()


def load_settings():
    for dir_path, _, files in os.walk('./data/'):
        for file in files:
            if file == "template.json":
                continue
            full_path = os.path.join(dir_path, file)
            try:
                settings_file = open(full_path, 'r')
            except OSError:
                print("Failed to load settings!")
                return False
            else:
                server_id = int(settings_file.readline().rstrip())
                server_settings = settings_file.readline()
                settings[server_id] = json.loads(server_settings)
    print("Settings loaded!")
    return True


def save_settings(guild):
    settings_str = json.dumps(settings.get(guild.id))
    try:
        file = open('data/{}.json'.format(guild.id), 'w')
    except OSError:
        return False
    else:
        file.writelines(["{}\n".format(guild.id), settings_str])
        file.close()
    return True


def validate_prefix(bot, message):
    server_id = message.guild.id
    server_settings = settings.get(server_id)
    if server_settings is None:
        return "fk!"
    return server_settings.get("prefix", "fk!")


def validate_user(user, channel, guild):
    user_permissions = channel.permissions_for(user)
    user_roles = user.roles
    if user_permissions.administrator:
        return True
    # is there a better way than this nested for loop?  map? list comprehension?
    for role in settings.get(guild.id).get("roles"):
        for user_role in user_roles:
            user_role_id = user_role.id
            if role == user_role_id:
                return True
    return False


def validate_channel(channel, guild):
    if not settings.get(guild.id).get("channels"):
        return True
    for c in settings.get(guild.id).get("channels"):
        if c == channel.id:
            return True
    return False


def get_stats_str(player_dict, stat_list):
    ret_str = ''
    try:
        for i in stat_list:
            ret_str += "`{:>17}: {:.5f}`\n".format(i, player_dict[i])
        return ret_str
    except KeyError:
        return ''


def print_player_fk(player_dict):
    err = None
    hit_str = get_stats_str(player_dict, hitting_stats)
    pit_str = get_stats_str(player_dict, pitching_stats)
    run_str = get_stats_str(player_dict, baserunning_stats)
    def_str = get_stats_str(player_dict, defense_stats)
    vib_str = get_stats_str(player_dict, vibe_stats)
    oth_str = get_stats_str(player_dict, other_stats)
    emb = discord.Embed(title=player_dict['name'])
    emb.add_field(name="Hitting:  {:.5f} Stars".format(player_dict["hittingRating"]*5), value=hit_str, inline=True)
    emb.add_field(name="Pitching:  {:.5f} Stars".format(player_dict["pitchingRating"]*5), value=pit_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.add_field(name="Baserunning:  {:.5f} Stars".format(player_dict["baserunningRating"]*5), value=run_str, inline=True)
    emb.add_field(name="Defense:  {:.5f} Stars".format(player_dict["defenseRating"]*5), value=def_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.add_field(name="Vibe", value=vib_str, inline=True)
    emb.add_field(name="Other", value=oth_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.set_footer(text=player_dict['id'])
    return err, emb


def get_player_stats(arg_str):
    player = cache.get_player(arg_str)
    return player


fk_bot = commands.Bot(command_prefix=validate_prefix)


@fk_bot.event
async def on_connect():
    load_settings()


@fk_bot.event
async def on_ready():
    print('log in as {0.user}'.format(fk_bot))


@fk_bot.event
async def on_guild_join(guild):
    settings[guild.id] = default_settings
    save_settings(guild)


@fk_bot.command(description="ping!")
async def ping(ctx):
    await ctx.send(random.choice(ping_strings))


# @fk_bot.command(description="channel test")
# async def channel(ctx, chn: discord.TextChannel):
#    await ctx.send("{0.mention}'s id is {0.id}".format(chn))


@fk_bot.group()
async def config(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Unrecognized Config Command!")


@config.command()
async def add(ctx, opt, tag):
    if not validate_user(ctx.author, ctx.channel, ctx.guild):
        await ctx.send("You are unauthorized to change my settings!")
        return
    if opt != "channel" and opt != "role":
        await ctx.send("Invalid add option. Try again with channel or role.")
        return
    tag = tag[1:-1]
    if opt == "channel":
        # channel format: #<numbers>
        tag = int(tag[1:])
        channel = ctx.guild.get_channel(int(tag))
        if channel is None:
            await ctx.send("Please tag a valid channel")
            return
        if int(tag) in settings[ctx.guild.id]["channels"]:
            await ctx.send("{0.mention} is already in my approved channels!".format(channel))
            return
        settings[ctx.guild.id]["channels"].append(int(tag))
        await ctx.send("Added {0.mention} to valid channels!".format(channel))
    else:
        # role format: @&<numbers>
        tag = int(tag[2:])
        role = ctx.guild.get_role(int(tag))
        if role is None:
            await ctx.send("Please tag a valid role")
            return
        if int(tag) in settings[ctx.guild.id]["roles"]:
            await ctx.send("{0.name} is already in my valid roles!".format(role))
            return
        settings[ctx.guild.id]["roles"].append(int(tag))
        await ctx.send("Added {0.name} to valid roles".format(role))
    save_settings(ctx.guild)
    return


@config.command()
async def remove(ctx, opt, tag):
    if not validate_user(ctx.author, ctx.channel, ctx.guild):
        await ctx.send("You are unauthorized to change my settings!")
        return
    if opt != "channel" and opt != "role":
        await ctx.send("Invalid remove option. Try again with channel or role.")
        return
    tag = tag[1:-1]
    if opt == "channel":
        tag = int(tag[1:])
        channel = ctx.guild.get_channel(tag)
        if channel is None:
            await ctx.send("Please tag a valid channel")
            return
        if tag not in settings[ctx.guild.id]["channels"]:
            await ctx.send("{0.mention} isn't in my approved channel list!".format(channel))
            return
        settings[ctx.guild.id]["channels"].remove(tag)
        await ctx.send("Removed {0.mention} from valid channels!".format(channel))
    else:
        tag = int(tag[2:])
        role = ctx.guild.get_role(tag)
        if role is None:
            await ctx.send("Please tag a valid role")
            return
        if tag not in settings[ctx.guild.id]["roles"]:
            await ctx.send("{0.name} isn't in my approved roles list!".format(role))
            return
        settings[ctx.guild.id]["roles"].remove(tag)
        await ctx.send("Removed {0.name} from valid roles!".format(role))
    save_settings(ctx.guild)
    return


@config.command()
async def prefix(ctx, arg):
    if not validate_user(ctx.author, ctx.channel, ctx.guild):
        await ctx.send("You are unauthorized to change my settings!")
        return
    if arg is None or arg == "":
        await ctx.send("No prefix specified!")
        return
    server_id = ctx.guild.id
    settings[server_id]["prefix"] = arg
    save_settings(ctx.guild)
    await ctx.send("fkBot prefix changed to {} [end of message]".format(arg))
    return


@config.command()
async def view(ctx):
    if not validate_user(ctx.author, ctx.channel, ctx.guild):
        await ctx.send("You're not an admin!")
        return
    guild_settings = settings[ctx.guild.id]
    guild_prefix = guild_settings["prefix"]
    guild_channels = ""
    guild_roles = ""
    for c in guild_settings["channels"]:
        channel = ctx.guild.get_channel(c)
        guild_channels += "{0.mention}\n".format(channel)
    if guild_channels == "":
        guild_channels = "None"
    for r in guild_settings["roles"]:
        role = ctx.guild.get_role(r)
        guild_roles += "{0.mention}\n".format(role)
    if guild_roles == "":
        guild_roles = "None"
    emb = discord.Embed(title="Settings for {0.name}".format(ctx.guild))
    emb.add_field(name="Prefix", value=guild_prefix)
    emb.add_field(name="Channels", value=guild_channels)
    emb.add_field(name="Roles", value=guild_roles)
    await ctx.send(embed=emb)
    return


@fk_bot.command(description="print a player's fk stats")
async def stats(ctx, *, player):
    if not validate_channel(ctx.channel, ctx.guild):
        await ctx.send("Can't use this here!")
        return
    pl_stats = get_player_stats(player)
    emb = None
    if pl_stats is not None:
        ret, emb = print_player_fk(pl_stats)
    else:
        ret = "I couldn't find {}!".format(player)
    if ret is not None:
        await ctx.send(ret)
    if emb is not None:
        await ctx.send(embed=emb)
    return


fk_bot.run(token)
