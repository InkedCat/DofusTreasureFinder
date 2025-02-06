import requests

class DofusDB:
    def __init__(self, token):
        self.__session = requests.Session()
        self.__session.headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': "fr-FR,fr;q=0.5",
                'Host': 'api.dofusdb.fr',
                'Origin': 'https://dofusdb.fr',
                'token': token,
                'referer': 'https://dofusdb.fr/',
            }
        )

    def get_hints(self, x, y, direction):
        r = self.__session.get('https://api.dofusdb.fr/treasure-hunt?x=' + str(x) + '&y=' + str(y) + '&direction=' + str(
            direction) + '&$limit=50&lang=fr')

        if r.status_code != 200:
            print('ERROR: Impossible de récupérer les indices')
            print('[' + str(r.status_code) + '] ' + r.reason)
            exit(1)

        hints = []
        for elt in reversed(r.json()['data']):
            hint = {'x': elt['posX'], 'y': elt['posY'], 'pois': []}

            for poi in elt['pois']:
                hint['pois'].append(poi['name']['fr'])

            hints.append(hint)

        return hints