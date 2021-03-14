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


fk_bot = commands.Bot(command_prefix="fk!")


@fk_bot.event
async def on_ready():
    print('log in as {0.user}'.format(fk_bot))


@fk_bot.command(description="ping!")
async def ping(ctx):
    await ctx.send(random.choice(ping_strings))


# @fk_bot.command(description="channel test")
# async def channel(ctx, chn: discord.TextChannel):
#    await ctx.send("{0.mention}'s id is {0.id}".format(chn))


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


@fk_bot.command(description="compare two players stats")
async def compare(ctx, player1, player2, stat):
    return

fk_bot.run(token)
