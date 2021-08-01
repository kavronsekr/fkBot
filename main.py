import discord
from discord.ext import commands
from player_cache import PlayerCache
from help import HelpCommand
import math
import datetime
import random
import os
import sys

print("Main: Initializing Cache!")
sys.stdout.flush()
cache = PlayerCache()

print("main: Loading bot token!")
sys.stdout.flush()
token = os.getenv("DISCORD_BOT_TOKEN")

ping_strings = ['Pong!', ':heartpulse:',
                'Taco Baco!', ':eyes:',
                ':ping_pong:', 'Please Imagine Music',
                'Thomas Dracaena hit a ground out to Edric Tosser',
                'Have you fed your hexbugs today?', 'The Breath Mints',
                'Chorby Short! Chorby Tall! Chorby swings at every ball!']

hitting_stats = ['trueHitting', 'hittingRating',
                 'divinity', 'martyrdom',
                 'moxie', 'musclitude',
                 'patheticism', 'thwackability',
                 'tragicness']
pitching_stats = ['truePitching', 'pitchingRating',
                  'coldness', 'overpowerment',
                  'ruthlessness', 'shakespearianism',
                  'suppression', 'unthwackability']
baserunning_stats = ['trueBaserunning', 'baserunningRating',
                     'baseThirst', 'continuation',
                     'groundFriction', 'indulgence',
                     'laserlikeness']
defense_stats = ['trueDefense', 'defenseRating',
                 'anticapitalism', 'chasiness',
                 'omniscience', 'tenaciousness',
                 'watchfulness']
vibe_stats = ['buoyancy', 'cinnamon', 'pressurization']
other_stats = ['totalFingers', 'peanutAllergy',
               'soul', 'eDensity', 'evolution']
all_stats = hitting_stats + pitching_stats + baserunning_stats + defense_stats + vibe_stats + other_stats

# h = hitting, b = baserunning, p = pitching, d = defense, v = vibes, o = other
comparison_keys = {"offensive": "h b", "defensive": "p d",
                   "offense": "h b",
                   "batting": "h", "hitting": "h",
                   "pitching": "p",
                   "baserunning": "b",
                   "defense": "d",
                   "all": "h p b d",
                   "vibes": "v", "other": "o"}

location_map = {"lineup": ["lineup"],
                "rotation": ["rotation"],
                "active": ["lineup", "rotation"],
                "shadows": ["shadows"],
                "all": ["lineup", "rotation", "shadows"]}

similar_index = ['hitting', 'pitching', 'baserunning', 'defense', 'all']


def get_stats_str(player_dict, stat_list):
    ret_str = ''
    try:
        for i in stat_list:
            ret_str += "`{:>20}: {:.3f}`\n".format(i, player_dict[i.lower()])
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
    update_time = datetime.datetime.fromtimestamp(player_dict['update_time']).strftime('%Y-%m-%d %H:%M:%S')
    player_name = player_dict['name']
    if 'unscatteredName' in player_dict['state'].keys():
        player_name = player_dict['state']['unscatteredName']
    emb = discord.Embed(title="{} -- {}".format(player_name, player_dict['id']))
    emb.add_field(name="Hitting:  {:.2f} ({:.2f}) Stars".format(
        player_dict["hittingrating"]*5, player_dict["truehitting"]*5), value=hit_str, inline=True)
    emb.add_field(name="Pitching:  {:.2f} ({:.2f}) Stars".format(
        player_dict["pitchingrating"]*5, player_dict["truepitching"]*5), value=pit_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.add_field(name="Baserunning:  {:.2f} ({:.2f}) Stars".format(
        player_dict["baserunningrating"]*5, player_dict["truebaserunning"]*5), value=run_str, inline=True)
    emb.add_field(name="Defense:  {:.2f} ({:.2f}) Stars".format(
        player_dict["defenserating"]*5, player_dict["truedefense"]*5), value=def_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.add_field(name="Vibe", value=vib_str, inline=True)
    emb.add_field(name="Other", value=oth_str, inline=True)
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    emb.set_footer(text="Last Updated: {}Z".format(update_time))
    return err, emb


def print_sorted_team(team, stat, team_map):
    err = None
    sorted_team = sorted(team_map.items(), key=lambda kv: (kv[1], kv[0]))
    sorted_team.reverse()
    emb = discord.Embed(title="{} by {}".format(team.title(), stat))
    name_str = ""
    stat_str = ""
    stat_total = 0
    for pair in sorted_team:
        name_str += "{}\n".format(pair[0])

        if stat != "peanutAllergy":
            stat_total += float(pair[1])
            stat_str += "{:.3f}\n".format(pair[1])
        else:
            stat_str += "{}\n".format(pair[1])
    if stat != "peanutAllergy":
        name_str += "\n"
        stat_str += "\n"
        name_str += "Team Average\n"
        stat_str += "{:.3f}\n".format(stat_total/len(sorted_team))

    emb.add_field(name="Player", value=name_str, inline=True)
    emb.add_field(name="{}".format(stat), value=stat_str, inline=True)
    return err, emb


def get_stat_list(index):
    if index == "h":
        return "Batting", hitting_stats
    if index == "p":
        return "Pitching", pitching_stats
    if index == "b":
        return "Baserunning", baserunning_stats
    if index == "d":
        return "Defense", defense_stats
    if index == "v":
        return "Vibes", vibe_stats
    if index == "o":
        return "Other", other_stats
    return "", []


def compare_stat(val1, val2, stat):
    if stat == "patheticism" or stat == "tragicness" or stat == "pressurization":
        return val2 > val1
    return val1 > val2


def print_player_comp(category, player1_dict, player2_dict):
    err = None
    cats = comparison_keys[category].split()
    title_string = ""
    pl1_string = ""
    pl2_string = ""
    for c in cats:
        title, stat_list = get_stat_list(c)
        if len(cats) > 1:
            title_string += "**{}**\n".format(title)
            pl1_string += "\u200B\n"
            pl2_string += "\u200B\n"
        if c != "o":
            for stat in stat_list:
                title_string += "\u200B\t\t{}:\n".format(stat)
                pl1_val = player1_dict[stat.lower()]
                pl2_val = player2_dict[stat.lower()]
                diff_val = pl2_val - pl1_val
                if compare_stat(pl1_val, pl2_val, stat):
                    pl1_string += "\u200B\t**{:.3f}**\n".format(pl1_val)
                    pl2_string += "\u200B\t{:.3f}\t".format(pl2_val)
                elif compare_stat(pl2_val, pl1_val, stat):
                    pl1_string += "\u200B\t{:.3f}\n".format(pl1_val)
                    pl2_string += "\u200B\t**{:.3f}**\t".format(pl2_val)
                else:
                    pl1_string += "\u200B\t{:.3f}\n".format(pl1_val)
                    pl2_string += "\u200B\t{:.3f}\t".format(pl2_val)
                pl2_string += "\u200B\t({:.3f})\n".format(diff_val)
        else:
            for stat in stat_list:
                title_string += "\u200B\t\t{}:\n".format(stat)
                pl1_val = player1_dict[stat.lower()]
                pl2_val = player2_dict[stat.lower()]
                pl1_string += "\u200B\t{}\n".format(pl1_val)
                pl2_string += "\u200B\t{}\n".format(pl2_val)
        title_string += "\u200B\n"
        pl1_string += "\u200B\n"
        pl2_string += "\u200B\n"
    player1_name = player1_dict["name"]
    if "unscatteredName" in player1_dict["state"].keys():
        player1_name = player1_dict["state"]["unscatteredName"]
    player2_name = player2_dict["name"]
    if "unscatteredName" in player2_dict["state"].keys():
        player2_name = player2_dict["state"]["unscatteredName"]
    emb = discord.Embed(title="{} vs. {}: {}".format(player1_name, player2_name, category.title()))
    emb.add_field(name="Stat", value=title_string, inline=True)
    emb.add_field(name="{}".format(player1_name), value=pl1_string, inline=True)
    emb.add_field(name="{}".format(player2_name), value=pl2_string, inline=True)
    return err, emb


def get_player_stats(arg_str):
    player = cache.get_player(arg_str)
    return player


def greedy_parse(arg_str, opt):
    if opt != "team" and opt != "player":
        return "", arg_str
    tokens = arg_str.split()
    current_str = ""
    largest_match = ""
    remainder_string = ""
    state = 2  # 2: no match, 1: match found, 0: greedy match confirmed
    for t in tokens:
        if state:
            if current_str:
                current_str += " "
            current_str += t
            if opt == "player":
                if cache.is_player(current_str) or cache.is_pid(current_str):
                    state = 1
                    largest_match = current_str
                elif state == 1:
                    state = 0
                    remainder_string = t
            else:
                if cache.is_team(current_str) or cache.is_tid(current_str):
                    state = 1
                    largest_match = current_str
                elif state == 1:
                    state = 0
                    remainder_string = t
        else:
            remainder_string += " {}".format(t)
    if not largest_match:
        remainder_string = arg_str
    return largest_match, remainder_string


def quote_parse_player(arg_str):
    left_ind = arg_str.find('"')
    right_ind = arg_str.find('"', left_ind + 1)
    if left_ind == -1 or right_ind == -1:
        return "", arg_str
    quote_str = arg_str[left_ind+1:right_ind]
    if not cache.is_player(quote_str) and not cache.is_pid(quote_str):
        return "", arg_str
    remainder = arg_str[right_ind + 1:]
    return quote_str, remainder


def calculate_rmse_dict(cat, player_cache, mod):
    full_cache = cache.get_cache()
    rms_dict = {}
    player_name = player_cache["name"]
    if "unscatteredName" in player_cache["state"].keys():
        player_name = player_cache["state"]["unscatteredName"]
    for pid, val in full_cache.items():
        val_name = val["name"]
        if "unscatteredName" in val["state"].keys():
            val_name = val["state"]["unscatteredName"]
        if val_name == player_name:
            continue  # don't compare against self
        if val["leagueteamid"] is None or val["leagueteamid"] == "c6c01051-cdd4-47d6-8a98-bb5b754f937f":
            continue  # don't compare to Hall Stars or Tournament Teams
        if "REPLICA" in val["permattr"]:
            continue  # don't compare to replicas
        counter = 0
        total = 0
        if cat == "hitting" or cat == "all":
            for stat in hitting_stats:
                if stat == "trueHitting" or stat == "hittingRating":
                    continue
                if stat == "patheticism" or stat == "tragicness":
                    stat_val = player_cache[stat.lower()] - mod
                    if stat_val > 0.999:
                        stat_val = 0.999
                else:
                    stat_val = player_cache[stat.lower()] + mod
                if stat_val < 0.001:
                    stat_val = 0.001
                total += (stat_val - val[stat.lower()]) ** 2
                counter += 1
        if cat == "pitching" or cat == "all":
            for stat in pitching_stats:
                if stat == "truePitching" or stat == "pitchingRating":
                    continue
                stat_val = player_cache[stat.lower()] + mod
                if stat_val < 0.001:
                    stat_val = 0.001
                total += (stat_val - val[stat.lower()]) ** 2
                counter += 1
        if cat == "baserunning" or cat == "all":
            for stat in baserunning_stats:
                if stat == "trueBaserunning" or stat == "baserunningRating":
                    continue
                stat_val = player_cache[stat.lower()] + mod
                if stat_val < 0.001:
                    stat_val = 0.001
                total += (stat_val - val[stat.lower()]) ** 2
                counter += 1
        if cat == "defense" or cat == "all":
            for stat in defense_stats:
                if stat == "trueDefense" or stat == "defenseRating":
                    continue
                stat_val = player_cache[stat.lower()] + mod
                if stat_val < 0.001:
                    stat_val = 0.001
                total += (stat_val - val[stat.lower()]) ** 2
                counter += 1
        rms_dict[val_name] = math.sqrt(total / counter)
    return rms_dict


def update_str_helper(new, old, stats):
    ret_str = ""
    change = False
    for stat in stats:
        lstat = stat.lower()
        diff = new[lstat] - old[lstat]
        if diff < 0:
            ret_str += "`{:>20}: {:.3f} ({:.3f})`\n".format(stat, new[lstat], diff)
            change = True
        elif diff > 0:
            ret_str += "`{:>20}: {:.3f} ({:.3f})`\n".format(stat, new[lstat], diff)
            change = True
        else:
            ret_str += "`{:>20}: {:.3f}`\n".format(stat, new[lstat])
    return ret_str, change


def form_update_summary(old, new):
    hit_str = ""
    pit_str = ""
    run_str = ""
    def_str = ""
    vib_str = ""
    oth_str = ""
    change = False

    if old is not None and new is not None:
        hit_str, hchange = update_str_helper(new, old, hitting_stats)
        pit_str, pchange = update_str_helper(new, old, pitching_stats)
        run_str, rchange = update_str_helper(new, old, baserunning_stats)
        def_str, dchange = update_str_helper(new, old, defense_stats)
        vib_str, vchange = update_str_helper(new, old, vibe_stats)
        oth_str, ochange = update_str_helper(new, old, other_stats)

        change = hchange or pchange or rchange or dchange or vchange or ochange
    else:
        return "No changes to report!", None

    if change:
        new_name = new['name']
        if 'unscatteredName' in new['state']:
            new_name = new['state']['unscatteredName']
        emb = discord.Embed(title="Summary of Changes to {}".format(new_name))
        emb.add_field(name="Hitting", value = hit_str, inline = True)
        emb.add_field(name="Pitching", value=pit_str, inline=True)
        emb.add_field(name="\u200B", value="\u200B", inline=True)
        emb.add_field(name="Baserunning", value=run_str, inline=True)
        emb.add_field(name="Defense", value=def_str, inline=True)
        emb.add_field(name="\u200B", value="\u200B", inline=True)
        emb.add_field(name="Vibes", value=vib_str, inline=True)
        emb.add_field(name="Other", value=oth_str, inline=True)
        emb.add_field(name="\u200B", value="\u200B", inline=True)

        return "", emb
    return "No changes to report!", None


print("main: Starting bot init!")
fk_bot = commands.Bot(command_prefix="fk!")
fk_bot.help_command = HelpCommand()


@fk_bot.event
async def on_ready():
    await fk_bot.change_presence(activity=discord.Game(name="fk!help"))
    print('log in as {0.user}'.format(fk_bot))


@fk_bot.command(description="Ping!",
                help="Check to see if I'm working!",
                brief="Pong!")
async def ping(ctx):
    await ctx.send(random.choice(ping_strings))


@fk_bot.command(aliases=["player", "st"],
                description="Print a player's hidden stats",
                usage="player",
                help="Prints out all of a player's hidden stats.\n" +
                     "Players can be specified by name or id, case insensitive.",
                brief="Print player stats")
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


@fk_bot.command(aliases=["comp", "cmp", "c"],
                description="Compare two players stats by stat category",
                usage="[category] player1 player2",  # Command arguments
                help="Prints a side by side comparison of two players.\n" +
                     "If category is specified, can be one of\n" +
                     "\t`all` - All star rated stats\n\t`offensive` - Hitting and Baserunning" +
                     "\n\t`defensive` - Pitching and Defense" +
                     "\n\t`batting`\n\t`pitching`\n\t" +
                     "`baserunning`\n\t`defense`\n\t`vibes`\n\t`other`\n" +
                     "If no category is specified, defaults to all.\n\n" +
                     "Player names can be quoted or unquoted and are non case sensitive.",
                brief="Compare players")
async def compare(ctx, *, arg_str):
    # We're going with the format [command] [category] [player1] [player2]
    # Quotes optional around player names.
    category, players = arg_str.split(maxsplit=1)
    # validate category
    category = category.lower()
    if category not in comparison_keys.keys():
        category = "all"
        players = arg_str
    # get and validate players
    player1, players = greedy_parse(players, "player")
    if player1 == "":
        player1, players = quote_parse_player(players)
        if player1 == "":
            await ctx.send("I couldn't parse that. Double check your input for typos, or consult `fk!help compare`")
            return
    player2, players = greedy_parse(players, "player")
    if player2 == "":
        player2, players = quote_parse_player(players)
        if player2 == "":
            await ctx.send("I couldn't parse that. Double check your input for typos, or consult `fk!help compare`")
            return
    pl1_stats = get_player_stats(player1)
    pl2_stats = get_player_stats(player2)
    ret, emb = print_player_comp(category, pl1_stats, pl2_stats)
    if ret is not None:
        await ctx.send(ret)
    if emb is not None:
        await ctx.send(embed=emb)
    return


@fk_bot.command(aliases=["team", "sr"],
                description="Sort a team in descending order by a stat",
                usage="team stat [location]",
                help="Provides a list of a team's players, sorted in descending order by a provided stat\n" +
                     "The team can be specified by name or team ID, case insensitive.\n" +
                     "The stat _is_ case sensitive and must be presented in the format specified in the site JSON.\n" +
                     "\tFor quicker reference, the stats can also be found in a stats query (`fk!stats`)\n" +
                     "A location can also be specified to narrow down which players are displayed.\n" +
                     "\tValid options are `lineup`, `rotation`, `active`, `shadows`, or `all`." +
                     "\tIf no location is supplied, all of a team's players will be sorted.",
                brief="Sort a team's players")
async def sort(ctx, *, arg_str):
    # format: fk!sort [team] [stat]
    team, rem = greedy_parse(arg_str, "team")
    if team == "":
        await ctx.send("I can't find that team!")
        return
    tokens = rem.split()
    if not len(tokens):
        await ctx.send("Invalid query. Please enter a stat after the team!")
        return
    stat = tokens[0]
    location = None
    if len(tokens) > 1:
        location = tokens[1]
    if stat not in all_stats:
        lower_stats = {k.lower() : k for k in all_stats}
        if stat.lower() not in lower_stats:
            await ctx.send("{} is not a recognized stat!".format(stat))
            return
        else:
            stat = lower_stats[stat.lower()]
    if location is not None:
        if location.lower() not in location_map.keys():
            await ctx.send("{} is not a valid location!".format(location))
            return
    else:
        location = "all"
    team_cache = cache.get_team(team)
    players = []
    for loc in location_map[location.lower()]:
        players += team_cache[loc]
    stat_map = dict()
    for p in players:
        player_dict = cache.get_player(p)
        if player_dict is None:
            print("Couldn't find player {}".format(p))
            continue
        player_name = player_dict["name"]
        if 'unscatteredName' in player_dict['state'].keys():
            player_name = player_dict['state']['unscatteredName']
        player_stat = player_dict[stat.lower()]
        stat_map[player_name] = player_stat
    team_name = team_cache['fullName']
    if 'scattered' in team_cache['state'].keys():
        team_name = team_cache['state']['scattered']['fullName']
    err, emb = print_sorted_team(team_name, stat, stat_map)
    if not err:
        await ctx.send(embed=emb)
    return


@fk_bot.command(aliases=["sim"],
                description="Find the five most similar players to another player, based on a stat group",
                usage="group player [stat offset]",
                help="Calculates the deviation between a player and all other players and returns the five most"
                     "similar.\nThe comparison is done on one of the major stat categories:\n"
                     "\tHitting, Pitching, Baserunning, Defense, or All.\n"
                     "The deviation is calculated by finding the Root Mean Square of all of the stats within the "
                     "category except for the star ratings (true and inflated).\n"
                     "A stat offset can be optionally added to all of the source player's stats, with a stat floor of "
                     "0.001.\n"
                     "This offset will be subtracted from patheticism and tragicness instead, and capped at 0.999 for"
                     "these two stats.\n\nCommon Stat Changes:\nInfuse: 0.20 to 0.40\nSun Dialed: 0.01\n"
                     "Entering Shadows: 0.04 - 0.09",
                brief="Find similar players")
async def similar(ctx, *, arg_str):
    arg_list = arg_str.split(maxsplit=1)
    if len(arg_list) < 2:
        await ctx.send("Not enough arguments specified! Remember to specify a group and a player!")
        return
    cat = arg_list[0]
    cat = cat.lower()
    arg_str = arg_list[1]
    if cat == "batting":
        cat = "hitting"
    if cat not in similar_index:
        await ctx.send("I didn't recognize that group. Valid groups are `hitting`, `pitching`, `baserunning`, `defense`"
                       ", or `all`")
        return
    player, mod_str = greedy_parse(arg_str, "player")
    if not cache.is_player(player):
        await ctx.send("I couldn't find that player!")
        return
    mod = 0
    if not mod_str == "":
        try:
            mod = float(mod_str)
        except ValueError:
            await ctx.send("I couldn't parse your stat modifier ({}). Treating it as 0!".format(mod_str))

    player_cache = cache.get_player(player)
    rms_dict = calculate_rmse_dict(cat, player_cache, mod)

    sorted_results = sorted(rms_dict.items(), key=lambda item: item[1])

    player_name = player_cache["name"]
    if "unscatteredName" in player_cache["state"].keys():
        player_name = player_cache["state"]["unscatteredName"]
    emb = discord.Embed(title="Similar Players to {} : {}".format(player_name, cat.title()))
    if mod:
        emb.description = "Applied a modifier of {} to all of {}'s stats!".format(mod, player_name)
    name_str = ""
    rms_str = ""
    for top in sorted_results[0:5]:
        name_str += "{}\n".format(top[0])
        rms_str += "{:.5f}\n".format(top[1])
    emb.add_field(name="Player", value=name_str, inline=True)
    emb.add_field(name="Deviation", value=rms_str, inline=True)
    await ctx.send(embed=emb)
    return


@fk_bot.command(description="Update a player's cache",
                usage="player",
                help="Updates the cached information for a player.\n" +
                     "Players can be specified by name or id, case insensitive.\n" +
                     "The command will fail if the player has been updated within the last minute.",
                brief="Update player")
async def update(ctx, *, arg_str):
    old_cache = cache.get_player(arg_str)
    ret_str = await cache.update_player(arg_str)
    new_cache = cache.get_player(arg_str)

    upd_str, emb = form_update_summary(old_cache, new_cache)

    await ctx.send(ret_str)
    if upd_str != "":
        await ctx.send(upd_str)
    if emb is not None:
        await ctx.send(embed=emb)
    return


print("main: Running bot!")
fk_bot.run(token)
