import requests, subprocess, time


API_KEY = '<Steam web api key>'
STEAMID = '<SteamID64 decimal>'


def get_playtime_required(api_key, steamid, verbose=False):
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steamid}&format=json'
    data = requests.get(url).json()
    if verbose:
        print(f"[INFO] Found {data['response']['game_count']} owned games on Steam")
    
    game_count = 0
    playtime_required = {playtime: [] for playtime in range(1, 12)}
    
    for game in data['response']['games']:
        overtime = game['playtime_forever'] % 12
        if overtime > 0:
            game_count += 1
            playtime_required[12 - overtime].append(game['appid'])
            if verbose:
                print(f"[GAME] APPID: {game['appid']:8d} | Playtime required: {12 - overtime:2d} min")
    if verbose:
        print(f"[INFO] Found {game_count} games to play")
    
    return {'game_count': game_count, 'playtime_required': playtime_required}


if __name__ == '__main__':
    while True:
        data = get_playtime_required(API_KEY, STEAMID, verbose=True)
        if data['game_count'] == 0:
            break
        
        pids = []
        
        for playtime in range(11, 0, -1):
            if len(data['playtime_required'][playtime]) == 0 and len(pids) == 0:
                continue
            
            for appid in data['playtime_required'][playtime]:
                pids.append(subprocess.Popen(['steam-idle.exe', f'{appid}']))
            time.sleep(60)
        
        for pid in pids:
            pid.terminate()
        
        time.sleep(60)
