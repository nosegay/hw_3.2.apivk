from urllib.parse import urlencode

import requests
import re


class Error(Exception):
    pass


class VKUser:
    def __init__(self, id, token=None):
        self.id = id
        self.token = token

    def __and__(self, other):
        get_friends_url = 'https://api.vk.com/method/friends.getMutual'
        params = {
            'v': '5.52',
            'access_token': self.token,
            'target_uid': other.id
        }

        response = requests.get(get_friends_url, params)
        try:
            friends = response.json()['response']
        except Exception as e:
            raise Error(f'Не удалось получить список общих друзей средствами API VK.\n{e}')

        mutual_friends = []
        for friend in friends:
            mutual_friends.append(VKUser(friend))

        return mutual_friends

    @staticmethod
    def get_access_token(api_id):
        oauth_url = 'https://oauth.vk.com/authorize'
        oauth_params = {
            'client_id': api_id,
            'display': 'page',
            'scope': 'friends',
            'response_type': 'token',
            'v': '5.52'
        }

        print('Для предоставления приложению доступа к списку Ваших друзей, пожалуйста, перейдите по ссылке:')
        print('?'.join((oauth_url, urlencode(oauth_params))))
        print('В открывшемся окне нажмите кнопку "Разрешить" '
              'и скопируйте URL-адрес, на который Вы будете перенаправлены.')
        url = input('Вставьте скопированный URL: ')

        token_re = re.compile('access_token=[0-9a-zA-Z]*')
        try:
            token = token_re.search(url).group(0)[13:]
        except Exception:
            raise Error(f'Не удалось извлечь ключ доступа из предоставленного URL.')

        user_id_re = re.compile('user_id=[0-9]*')
        try:
            user_id = user_id_re.search(url).group(0)[8:]
        except Exception:
            raise Error(f'Не удалось извлечь ID пользователя из предоставленного URL.')

        return user_id, token

    def __str__(self):
        return f'https://vk.com/id{self.id}'


if __name__ == '__main__':
    api_id = int(input('Для работы программы необходимо ввести API_ID: '))

    try:
        user_id, token = VKUser.get_access_token(api_id)
        main_user = VKUser(user_id, token)
    except Error as e:
        print(e)

    another_id = input('Введите ID пользователя для поиска общих друзей: ')
    another_user = VKUser(another_id)

    mutual_friends = main_user & another_user
    for friend in mutual_friends:
        print(friend)
