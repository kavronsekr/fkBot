import discord
from player_cache import PlayerCache
import aiohttp
import asyncio
import json

cache = PlayerCache(3600)
client = discord.Client()
token = ""

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


@client.event
async def on_ready():
    print('log in as {0.user}'.format(client))
    await cache.start()


@client.event
async def on_message(message):
    if not message.content.startswith('fk!'):
        return
    if message.author == client.user:
        return
    tkns = message.content.split(None, 1)
    cmd = tkns[0]
    ret = None
    emb = None
    if cmd == 'fk!hello':
        ret = 'Hello!'
    elif cmd == 'fk!stats':
        stats = get_player_stats(tkns[1])
        if stats is not None:
            ret, emb = print_player_fk(stats)
        else:
            ret = "I couldn't find {}!".format(tkns[1])
    elif cmd == 'fk!set':
        ret = ""
    if ret is not None:
        await message.channel.send(ret)
    if emb is not None:
        await message.channel.send(embed=emb)


client.run(token)
