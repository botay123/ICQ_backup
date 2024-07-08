import json
import logging
import os
from typing import List

import requests

from config import Buddie, settings, UserConfig


def get_contacts_from_json(ME=False) -> List[Buddie]:
    """Получаем список контактов"""
    with open(settings.uset_contacts, 'r', encoding='utf-8') as f:
        text = f.read()

    data = json.loads(text)

    if ME:
        me = data.get('response').get('data').get('events')[1].get('eventData')
        return [Buddie(aimId=me.get('aimId'),
                       userType=me.get('userType'),
                       chatType=me.get('chatType'),
                       friendly=me.get('friendly')
                       )]

    # список контактов
    buddies = []

    for group in data.get('response').get('data').get('events')[0].get('eventData').get('groups'):
        for buddie in group.get('buddies'):

            if buddie.get('userType') == 'sms' or buddie.get('aimId') is None:
                continue

            buddies.append(Buddie(aimId=buddie.get('aimId'),
                                  userType=buddie.get('userType'),
                                  chatType=buddie.get('chatType'),
                                  friendly=buddie.get('friendly')
                                  )
                           )

    return buddies


def getChatInfo(session: requests.Session, contact: Buddie, folders: dict, user_config: UserConfig):
    if contact.userType == 'icq':
        url = 'https://u.icq.net/api/v92/rapi/getUserInfo'

    elif contact.userType == 'chat':
        url = 'https://u.icq.net/api/v92/rapi/getChatInfo'
    else:
        return

    # payload = '{"reqId":"' + user_config.request_data.reqId + '","aimsid":"' + user_config.request_data.aimsid + '","params":{"sn":"' + chatId + '","memberLimit":200}}'
    payload = '{"reqId":"' + user_config.request_data.reqId + '","aimsid":"' + user_config.request_data.aimsid + '","params":{"sn":"' + contact.aimId + '"}}'

    r = session.post(url,
                     data=payload,
                     headers=user_config.headers,
                     cookies=user_config.cookies
                     )

    data = json.dumps(r.json(), indent=4, ensure_ascii=False)
    with open(f"{folders.get('contact_path')}/chatInfo.json", 'w+', encoding="utf-8") as f:
        f.write(data)


def getFolders(contact: Buddie) -> dict:
    if contact.friendly != '':
        name = contact.friendly
    else:
        name = contact.aimId

    # sub криво работает на windows, костыль
    # name = re.sub(r'[^\w_. -]', '_', name)
    name = name.replace('.', '_')
    name = name.replace(',', '_')
    name = name.replace('-', '_')
    name = name.replace(' ', '_')
    name = name.replace('/', '_')
    name = name.replace('\\', '_')
    name = name.replace(':', '_')
    name = name.replace(';', '_')
    name = name.replace('"', '_')
    name = name.replace("'", '_')

    if not os.path.exists(settings.directory):
        os.makedirs(settings.directory)

    contact_path = f'{settings.directory}/{name}'

    if not os.path.exists(contact_path):
        os.makedirs(contact_path)

    json_path = f'{contact_path}/json'

    if not os.path.exists(json_path):
        os.makedirs(json_path)

    img_path = f'{contact_path}/files'

    if not os.path.exists(img_path):
        os.makedirs(img_path)

    return {'contact_path': contact_path,
            'json_path': json_path,
            'name': name,
            'img_path': img_path}


def contacts_from_filter():
    data = []
    if not os.path.exists(settings.uset_filter):
        return data

    else:
        with open(settings.uset_filter, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                items = line.split('|')
                data.append(Buddie(aimId=items[0],
                                   userType=items[1],
                                   chatType=items[2],
                                   friendly=items[3].strip()
                                   ))
    return data


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(settings.uset_logs, 'a+', encoding='utf-8')
    handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))

    logger.addHandler(handler)

    return logger
