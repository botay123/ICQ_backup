import json
import os
import re
from pathlib import Path
from datetime import datetime

from utils import get_contacts_from_json


def getChatInfo() -> dict:
    cwd = os.getcwd()
    os.chdir('..')
    contacts = get_contacts_from_json()
    me = get_contacts_from_json(ME=True)

    members_map = {}
    for member in contacts:
        # firstName = member.get('anketa').get('firstName')
        # lastName = member.get('anketa').get('lastName')
        # sn = member.get('anketa').get('sn')

        members_map.update({member.aimId: {'aimId': member.aimId,
                                           'friendly': member.friendly,

                                           }})
    members_map.update({me[0].aimId: {'aimId': me[0].aimId,
                                      'friendly': me[0].friendly,

                                      }})
    os.chdir(cwd)
    return members_map


def parseGroup(folder='Развитие_E___'):
    results = []
    members_map = getChatInfo()

    files = os.listdir(f'{BASE_DIR}/results/{folder}/json/')
    map = {}

    for file in files:
        map.update({str(re.search(r'data_(\d+).json', file).group(1)): file})

    for i in range(1, len(files)):
        file = map.get(str(i))
        print(file)

        with open(f'{BASE_DIR}/results/{folder}/json/{file}', 'r') as f:
            data = json.load(f)

        for msg in data:
            DATE = datetime.fromtimestamp(msg.get('time')).strftime('%d.%m.%Y, %H:%M:%S')
            TEXT = msg.get('text')
            SENDER = msg.get('chat').get('sender')

            USER = members_map.get(SENDER).get('friendly')

            results.append(data_format.get('message').format(**{
                'DATE': DATE,
                'TEXT': TEXT,
                'USER': USER,
            }))
    
    with open(f'{folder}/_chat.txt', 'w+') as f:
        f.write('\n'.join(list(reversed(r))))
    
    return 


def parseChat(folder='Мансур'):
    results = []
    ME = 'Константин'
    PERSON = 'Мансур'

    files = os.listdir(f'{BASE_DIR}/results/{folder}/json/')
    map = {}

    for file in files:
        map.update({str(re.search(r'data_(\d+).json', file).group(1)): file})

    for i in range(1, len(files)):
        file = map.get(str(i))
        print(file)

        with open(f'{BASE_DIR}/results/{folder}/json/{file}', 'r') as f:
            data = json.load(f)

        for msg in data:
            DATE = datetime.fromtimestamp(msg.get('time')).strftime('%d.%m.%Y, %H:%M:%S')
            TEXT = msg.get('text')

            if msg.get('outgoing'):
                USER = ME
            else:
                USER = PERSON

            results.append(data_format.get('message').format(**{
                'DATE': DATE,
                'TEXT': TEXT,
                'USER': USER,
            }))

    return results


if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent.parent
    data_format = {
        'file': '[{DATE}] {USER}: ‎<прикреплено: {FILE_NAME}>',
        'message': '[{DATE}] ~ {USER}: {TEXT}',  # 21.10.2020, 10:01:22
    }

    parseGroup()
    # getChatInfo()
    # print(data_format.get('message'))
    # r = parseChat()

    # print('\n'.join(list(reversed(r))))
    
