import requests as request
import os

from mapper.map_dto import map_object
from helper.publisher import publish

base_url = os.getenv('BASE_URL')
token = os.getenv('TOKEN')


def lambda_handler(event, context):
    print(event, context)
    print("mapping object...")

    try:
        items = map_object(event)
        print("Object: ", items)
        print("calling Loterias API...")

        for i in items:
            payload = {'loteria': i['loteria'], 'token': token, 'concurso': i['concurso']}
            response = request.get(base_url, payload)
            print(response.json())
            games_user = i['games']
            print("Games User: ", games_user)
            r = response.json()
            if int(r['numero_concurso']) != int(i['concurso']):
                raise Exception("Número do concurso não disponível ou ainda não efetuado sorteio. Tente novamente"
                                " mais tarde!")
            dezenas_sorteadas = r['dezenas']
            wzero = [ele.lstrip('0') for ele in dezenas_sorteadas]
            print("Dezenas Sorteadas: ", wzero)
            final_list = []
            for game in games_user:
                lista_acertos = []
                print("GAME: ", game)
                for dezena in wzero:
                    for x in game:
                        if x['N'] == dezena:
                            lista_acertos.append(x)
                resultado = {
                    'jogo': game,
                    'concurso': r['numero_concurso'],
                    'Dezenas Sorteadas': dezenas_sorteadas,
                    'Total de acertos': len(lista_acertos)
                }
                final_list.append(resultado)

            print("Lista de acerto final: ", final_list)
            publish(final_list)

        return {
            'code': 200
        }

    except Exception as error:
        return {'code': 500, 'message': str(error)}
