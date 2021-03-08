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

hitting_stats = ['divinity', 'martyrdom',
                 'moxie', 'musclitude',
                 'patheticism', 'thwackability',
                 'tragicness', 'hittingRating']
pitching_stats = ['coldness', 'overpowerment',
                  'ruthlessness', 'shakespearianism',
                  'suppression', 'unthwackability',
                  'pitchingRating']
baserunning_stats = ['baseThirst', 'continuation',
                     'groundFriction', 'indulgence',
                     'laserlikeness', 'baserunningRating']
defense_stats = ['anticapitalism', 'chasiness',
                 'omniscience', 'tenaciousness',
                 'watchfulness', 'defenseRating']
vibe_stats = ['buoyancy', 'cinnamon', 'pressurization']
other_stats = ['totalFingers', 'peanutAllergy',
               'soul']

default_settings = {"prefix": "fk!",
                    "channels": [],
                    "roles": []
                    }
settings = dict()


def validate_prefix(bot, message):
    server_id = message.guild.id
    server_settings = settings.get(server_id)
    if server_settings is None:
        return "fk!"
    return server_settings.get("prefix", "fk!")


def load_settings():
    for dir_path, _, files in os.walk('./data/'):
        for file in files:
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
    if channel in settings.get(guild.id).get("channels"):
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
    emb.add_field(name="Hitting", value=hit_str, inline=True)
    emb.add_field(name="Pitching", value=pit_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.add_field(name="Baserunning", value=run_str, inline=True)
    emb.add_field(name="Defense", value=def_str, inline=True)
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
        tag = tag[1:]
        channel = ctx.guild.get_channel(int(tag))
        if channel is None:
            await ctx.send("Please tag a valid channel")
            return
        settings[ctx.guild.id]["channels"].append(int(tag))
        await ctx.send("Added {0.mention} to valid channels!".format(channel))
        return
    else:
        # role format: @&<numbers>
        tag = tag[2:]
        role = ctx.guild.get_role(int(tag))
        if role is None:
            await ctx.send("Please tag a valid role")
            return
        settings[ctx.guild.id]["roles"].append(int(tag))
        await ctx.send("Added {0.mention} to valid roles".format(role))
        return
    return


@config.command()
async def remove(ctx, opt, tag):
    if not validate_user(ctx.author, ctx.channel, ctx.guild):
        await ctx.send("You are unauthorized to change my settings!")
        return
    if opt != "channel" and opt != "role":
        await ctx.send("Invalid remove option. Try again with channel or role.")
        return
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
    # TODO: Make an embed or otherwise print out the prefix, channels, roles
    return


@fk_bot.command(description="print a player's fk stats")
async def stats(ctx, *, player):
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
