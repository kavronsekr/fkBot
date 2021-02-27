import discord
from discord.ext import commands
from player_cache import PlayerCache
import os
import random
import aiohttp
import asyncio
import json

cache = PlayerCache()

token_filename = 'tokens.txt'
token_file = open(token_filename, 'r')
token = token_file.readline()

ping_strings = ['Pong!', ':heartpulse:',
                'Taco Baco!', ':eyes:',
                ':ping_pong:',
                'Thomas Dracaena hit a ground out to Edric Tosser']

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
                    "channels": None,
                    "roles": None
                    }
settings = dict()


def prefix(bot, message):
    server_id = message.guild.id
    return settings.get(server_id, 'fk!')


def load_settings():
    dir_path, _, files = os.walk('./data/')
    for file in files:
        full_path = os.path.join(dir_path, file)
        settings_file = open(full_path, 'r')
        server_id = settings_file.readline()
        server_settings = settings_file.readline()
        settings[server_id] = json.loads(server_settings)
    return


fk_bot = commands.Bot(command_prefix=prefix)


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


@fk_bot.event
async def on_ready():
    print('log in as {0.user}'.format(fk_bot))


@fk_bot.event
async def on_guild_join(guild):
    settings[guild.id] = default_settings
    settings_str = json.dumps(default_settings)
    file = open('data/{}.json'.format(guild.id), 'w')
    file.writelines(["{}\n".format(guild.id), settings_str])
    file.close()


@fk_bot.command(description="ping!")
async def ping(ctx):
    await ctx.send(random.choice(ping_strings))


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
