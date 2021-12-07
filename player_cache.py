import json
import aiohttp
import time
from discord.ext import tasks

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
               'soul', 'evolution']
all_stats = hitting_stats + pitching_stats + baserunning_stats + defense_stats + vibe_stats + other_stats

sc_teams = ["505ae98b-7d85-4f51-99ef-60ccd7365d97",
            "6f9ff34d-825f-477b-8600-1cec4febaecf",
            "a94de6ef-5fc9-4470-89a0-557072fe4daf",
            "d2949bd0-6a28-4e0d-aa07-cecc437cbd99",
            "5371833b-a620-4952-b2cb-a15eed8ad183",
            "30c9bcd2-cc5a-421d-97d0-d39fefad053a",
            "93f91157-f628-4c9a-a392-d2b1dbd79ac5",
            "f0ec8435-0427-4ffd-ad0c-a67f60a75e0e",
            "9da5c6b8-ccad-4bb5-b6b8-dc1d6b8ca6ed",
            "7dc37924-0bb8-4e40-a826-c497d51e447c",
            "36f4efea-9d27-4457-a7b4-4b45ad2e23a3",
            "9a2f6bb9-c72c-437c-a3c4-e076dc5d10d4",
            "5818fb9b-f191-462e-9085-6fe311aaaf70",
            "fab9420f-0730-4054-bd17-355113f204c2",
            "22d8a1e9-e679-4bde-ae8a-318cb591d1c8",
            "8b38afb3-2e20-4e73-bb00-22bab14e3cda",
            "3d858bda-dcef-4d05-928e-6557d3123f17",
            "3a4412d6-5404-4801-bf06-81cb7884fae4",
            "ee722cbd-812f-4525-81d7-dfa89fb867a4",
            "19f81c84-9a94-49fa-9c23-2e1355126250",
            "79347640-8d5d-4e41-819d-2b0c86f20b76",
            "b1a50aa9-c515-46e8-8db9-d5378840362c",
            "0706f3cf-d6c4-4bd0-ac8c-de3d75ffa77e",
            "045b4b38-fb11-4fa6-8dc0-f75997eacd28"]

def add_true_ratings(player_dict):
    term1 = 1 - player_dict["tragicness"]
    term2 = 1 - player_dict["patheticism"]
    term3 = player_dict["thwackability"] * player_dict["divinity"]
    term4 = player_dict["moxie"] * player_dict["musclitude"]
    term5 = player_dict["martyrdom"]
    true_rating = pow(term1, 0.01) * pow(term2, 0.05) * pow(term3, 0.35) * pow(term4, 0.075) * pow(term5, 0.02)
    player_dict["trueHitting"] = true_rating
    term1 = player_dict["unthwackability"]
    term2 = player_dict["ruthlessness"]
    term3 = player_dict["overpowerment"]
    term4 = player_dict["shakespearianism"]
    term5 = player_dict["coldness"]
    true_rating = pow(term1, 0.5) * pow(term2, 0.4) * pow(term3, 0.15) * pow(term4, 0.1) * pow(term5, 0.025)
    player_dict["truePitching"] = true_rating
    term1 = player_dict["laserlikeness"]
    term2 = player_dict["baseThirst"] * player_dict["continuation"] * player_dict["groundFriction"] * player_dict[
        "indulgence"]
    true_rating = pow(term1, 0.5) * pow(term2, 0.1)
    player_dict["trueBaserunning"] = true_rating
    term1 = player_dict["omniscience"] * player_dict["tenaciousness"]
    term2 = player_dict["watchfulness"] * player_dict["anticapitalism"] * player_dict["chasiness"]
    true_rating = pow(term1, 0.2) * pow(term2, 0.1)
    player_dict["trueDefense"] = true_rating
    return


class PlayerCache:
    def __init__(self):
        self.player_cache = dict()
        self.player_map = dict()
        self.player_ids = set()

        self.team_cache = dict()
        self.team_map = dict()
        self.team_ids = set()

        self.sc_cache_loop.start()
        return

    def is_player(self, player):
        names = self.player_map.keys()
        return player.lower() in names

    def is_pid(self, pid):
        return pid.lower() in self.player_ids

    def is_team(self, team):
        names = self.team_map.keys()
        return team.lower() in names

    def is_tid(self, tid):
        return tid.lower() in self.team_ids

    @tasks.loop(seconds=3600)
    async def cache_loop(self):
        print("cache_loop: Spawning ClientSession")
        async with aiohttp.ClientSession() as session:
            print("cache_loop: Connecting to blaseball/sibr")
            async with session.get('https://api.blaseball.com/database/allTeams') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for team in data:
                        team_id = team['id']
                        self.team_ids.update(team_id)
                        if 'scattered' in team['state'].keys():
                            self.team_map[team['state']['scattered']['fullName'].lower()] = team_id
                            self.team_map[team['state']['scattered']['location'].lower()] = team_id
                            self.team_map[team['state']['scattered']['nickname'].lower()] = team_id
                        else:
                            self.team_map[team['fullName'].lower()] = team_id
                            self.team_map[team['location'].lower()] = team_id
                            self.team_map[team['nickname'].lower()] = team_id
                        self.team_map[team['shorthand'].lower()] = team_id
                        self.team_cache[team_id] = team

                        self.player_ids.update(team['lineup'])
                        self.player_ids.update(team['rotation'])
                        self.player_ids.update(team['shadows'])

                else:
                    print("Bad response " + str(resp.status))
                    return
            async with session.get('https://api.sibr.dev/chronicler/v1/players/names') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for pid, name in data.items():
                        self.player_ids.add(pid)
                        self.player_map[name.lower()] = pid
                else:
                    print("Bad response " + str(resp.status))
                    return
        print(str(len(self.player_ids)) + " loaded!")
        await self.form_cache()
        return

    # a short circuit version of the cache loop
    @tasks.loop(seconds=3600)
    async def sc_cache_loop(self):
        print("sc_cache_loop: Spawning ClientSession")
        async with aiohttp.ClientSession() as session:
            print("sc_cache_loop: looping over sc teams")
            for team in sc_teams:
                async with session.get('https://api.blaseball.com/database/team?id=' + team) as resp:
                    if resp.status == 200:
                        data = json.loads(await resp.text())
                        team_id = data['id']
                        self.team_ids.update(team_id)
                        if 'scattered' in data['state'].keys():
                            self.team_map[data['state']['scattered']['fullName'].lower()] = team_id
                            self.team_map[data['state']['scattered']['location'].lower()] = team_id
                            self.team_map[data['state']['scattered']['nickname'].lower()] = team_id
                        else:
                            self.team_map[data['fullName'].lower()] = team_id
                            self.team_map[data['location'].lower()] = team_id
                            self.team_map[data['nickname'].lower()] = team_id
                        self.team_map[data['shorthand'].lower()] = team_id
                        self.team_cache[team_id] = data

                        self.player_ids.update(data['lineup'])
                        self.player_ids.update(data['rotation'])
                        self.player_ids.update(data['shadows'])
                    else:
                        print("Bad response " + str(resp.status))
                        return
            async with session.get('https://api.sibr.dev/chronicler/v1/players/names') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for pid, name in data.items():
                        self.player_ids.add(pid)
                        self.player_map[name.lower()] = pid
                else:
                    print("Bad response " + str(resp.status))
                    return
        print(str(len(self.player_ids)) + " loaded!")
        await self.form_cache()
        return

    async def form_cache(self, players=None):
        if players is None:
            plist = list(self.player_ids)
        else:
            plist = list()
            plist.append(players)
        async with aiohttp.ClientSession() as session:
            for split_list in [plist[i:i + 100] for i in range(0, len(plist), 100)]:
                req_str = ','.join(split_list)
                async with session.get('https://api.blaseball.com/database/players?ids=' + req_str) as resp:
                    if resp.status == 200:
                        data = json.loads(await resp.text())
                        update_time = int(time.time())
                        for p in data:
                            pid = p['id']
                            add_true_ratings(p)
                            for stat in all_stats:
                                if p[stat] is None:
                                    p[stat] = 0
                            self.player_cache[pid] = {k.lower() : v for k, v in p.items()}
                            self.player_cache[pid]['update_time'] = update_time
                            self.player_map[p['name'].lower()] = pid
                            if 'unscatteredName' in p['state'].keys():
                                self.player_map[p['state']['unscatteredName'].lower()] = pid
                    else:
                        print("Bad response " + str(resp.status))
                        return
        print("Players Cached!")

    def get_player(self, key):
        if key in self.player_cache.keys():
            return self.player_cache[key]
        elif str(key).lower() in self.player_map.keys():
            return self.player_cache[self.player_map[key.lower()]]
        else:
            return None

    def get_team(self, key):
        if key in self.team_cache.keys():
            return self.team_cache[key]
        elif str(key).lower() in self.team_map.keys():
            return self.team_cache[self.team_map[key.lower()]]
        else:
            return None

    def get_cache(self):  # Ok, but why would you do this.
        return self.player_cache

    async def update_player(self, key):
        key = key.lower()
        if key in self.player_cache.keys():
            player_id = key
            player_name = self.player_cache[key]['name']
            if 'unscatteredName' in self.player_cache[key]['state'].keys():
                player_name = self.player_cache[key]['state']['unscatteredName']
        elif key in self.player_map.keys():
            player_id = self.player_map[key]
            player_name = self.player_cache[player_id]['name']
            if 'unscatteredName' in self.player_cache[player_id]['state'].keys():
                player_name = self.player_cache[player_id]['state']['unscatteredName']
        else:
            return "I couldn't find that player! If they were just hatched, it'll take me some time to find them..."
        cur_time = int(time.time())
        # if (cur_time - self.player_cache[player_id]["update_time"]) < 60:
        #    return "I've updated this player within the last minute!"
        await self.form_cache(players=player_id)
        return "Updated the data for {}!".format(player_name)

