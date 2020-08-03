import requests

def get_riot_id_icon(name):
    header = {
...     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
...     "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
...     "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
...     "Origin": "https://developer.riotgames.com",
...     "X-Riot-Token": "RGAPI-91b47991-850e-41b7-a3fb-59b7a30b1a56"
... }
    url = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/'
    result = requests.get(url + name, headers = headers)
    if result.status_code == 200:
        return result.json['profileIconId']
    else:
        return None