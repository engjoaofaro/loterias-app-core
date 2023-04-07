import json


megasena = (1, 'megasena')
lotofacil = (2, 'lotofacil')
lotomania = (3, 'lotomania')


def map_object(event):
    items = event['Items']
    games_user = []

    for i in items:
        game_type = i['gameType']['N']
        if game_type == '1':
            game_type = megasena[1]
        if game_type == '2':
            game_type = lotofacil[1]
        if game_type == '3':
            game_type = lotomania[1]
        id_transaction = i['voucher']['S']
        lottery_number = i['lotteryNumber']['N']
        email = i['email']['S']
        games = []
        for x in i['games']['L']:
            games.append(x['L'])
        item = {
            'loteria': game_type,
            'id': id_transaction,
            'concurso': lottery_number,
            'email': email,
            'games': games
        }
        games_user.append(item)

    return games_user



