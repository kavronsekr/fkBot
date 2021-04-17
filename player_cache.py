import json
import asyncio
import aiohttp
import time
from discord.ext import tasks


class PlayerCache:
    def __init__(self):
        self.player_cache = dict()
        self.player_map = dict()
        self.player_ids = set()

        self.team_cache = dict()
        self.team_map = dict()
        self.team_ids = set()

        self.cache_loop.start()
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
        async with aiohttp.ClientSession() as session:
            async with session.get('https://blaseball.com/database/allTeams') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for team in data:
                        team_id = team['id']
                        self.team_ids.update(team_id)
                        self.team_map[team['fullName'].lower()] = team_id
                        self.team_map[team['location'].lower()] = team_id
                        self.team_map[team['nickname'].lower()] = team_id
                        self.team_map[team['shorthand'].lower()] = team_id
                        self.team_cache[team_id] = team

                        self.player_ids.update(team['lineup'])
                        self.player_ids.update(team['rotation'])
                        self.player_ids.update(team['bullpen'])
                        self.player_ids.update(team['bench'])
                else:
                    print("Bad response " + str(resp.status))
                    return
            async with session.get('https://www.blaseball.com/api/getTribute') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for p in data:
                        self.player_ids.add(p['playerId'])
                else:
                    print("Bad response " + str(resp.status))
                    return
        print(str(len(self.player_ids)) + " loaded!")
        await self.form_cache()
        return

    async def form_cache(self, players=None):
        if players is None:
            players = self.player_ids
        plist = list(players)
        async with aiohttp.ClientSession() as session:
            for split_list in [plist[i:i + 100] for i in range(0, len(plist), 100)]:
                req_str = ','.join(split_list)
                async with session.get('https://blaseball.com/database/players?ids=' + req_str) as resp:
                    if resp.status == 200:
                        data = json.loads(await resp.text())
                        update_time = int(time.time())
                        for p in data:
                            pid = p['id']
                            lc_name = p['name'].lower()
                            self.player_map[lc_name] = pid
                            self.player_cache[pid] = p
                            self.player_cache[pid]['update_time'] = update_time
                    else:
                        print("Bad response " + str(resp.status))
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

    async def update_player(self, key):
        if key in self.player_cache.keys():
            player_id = key
            player_name = self.player_cache[key]['name']
        elif key in self.player_map.keys():
            player_id = self.player_map[key]
            player_name = key
        else:
            return "I couldn't find that player! If they were just hatched, it'll take me some time to find them..."
        await self.form_cache(player_id)
        return "Updated the data for {}!".format(player_name)

