import json
import asyncio
import aiohttp
import time


class PlayerCache:
    def __init__(self, interval):
        self.player_cache = dict()
        self.player_map = dict()
        self.player_ids = set()

        self.is_started = False
        self.interval = interval
        self._task = None
        return

    async def start(self):
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.ensure_future(self._run())

    async def get_player_ids(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://blaseball.com/database/allTeams') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for team in data:
                        self.player_ids.update(team['lineup'])
                        self.player_ids.update(team['rotation'])
                        self.player_ids.update(team['bullpen'])
                        self.player_ids.update(team['bench'])
                else:
                    print("Bad response" + str(resp.status))
            async with session.get('https://www.blaseball.com/api/getTribute') as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    for p in data:
                        self.player_ids.add(p['playerId'])
                else:
                    print("Bad response " + str(resp.status))
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
                            self.player_map[p['name']] = pid
                            self.player_cache[pid] = p
                            self.player_cache[pid]['update_time'] = update_time
                    else:
                        print("Bad response " + str(resp.status))
        print("Players Cached!")

    def get_player(self, key):
        if key in self.player_cache.keys():
            return self.player_cache[key]
        elif key in self.player_map.keys():
            return self.player_cache[self.player_map[key]]
        else:
            return None

    async def _run(self):
        while True:
            await self.get_player_ids()
            await asyncio.sleep(self.interval)
