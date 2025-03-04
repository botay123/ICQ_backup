import sys
sys.path.append('..')

import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from tqdm import tqdm

from config import settings
from utils import get_contacts_from_json
from PIL import Image


def getChatInfo() -> dict:
    cwd = os.getcwd()
    os.chdir('..')
    contacts = get_contacts_from_json()
    me = get_contacts_from_json(ME=True)

    members_map = {}
    for member in contacts:
        members_map.update({member.aimId: {'aimId': member.aimId,
                                           'friendly': member.friendly,

                                           }})
    members_map.update({me[0].aimId: {'aimId': me[0].aimId,
                                      'friendly': me[0].friendly,

                                      }})
    os.chdir(cwd)
    return members_map


def createFolders(name: str) -> str:
    if not os.path.exists(settings.directory):
        os.makedirs(settings.directory)

    if not os.path.exists(f'{settings.directory}/{name}'):
        os.makedirs(f'{settings.directory}/{name}')

    return f'{settings.directory}/{name}'


def parseGroup(folder: str):
    dst_folder = createFolders(folder)
    results = []
    members_map = getChatInfo()

    files = os.listdir(f'{BASE_DIR}/results/{folder}/json/')
    map = {}
    IMG_COUNT = 3

    for file in files:
        map.update({str(re.search(r'data_(\d+).json', file).group(1)): file})

    for i in tqdm(range(1, len(files))):
        file = map.get(str(i))
        # print(file)

        with open(f'{BASE_DIR}/results/{folder}/json/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for msg in data:
            DATE = datetime.fromtimestamp(msg.get('time')).strftime('%d.%m.%Y, %H:%M:%S')
            TEXT = msg.get('text')
            SENDER = msg.get('chat', {}).get('sender')

            USER = members_map.get(SENDER, {}).get('friendly', SENDER)

            TEXT_parts = None
            if msg.get('parts'):
                for parts in msg.get('parts'):

                    if parts.get('mediaType') == 'quote':
                        # забиваем на цитату, не подходит формат
                        continue

                    if parts.get('captionedContent'):
                        # только текст, чтобы не парсить
                        TEXT_parts = parts.get('captionedContent', {}).get('caption')
                    else:
                        TEXT_parts = parts.get('text')

                    if TEXT_parts:
                        if 'files.icq.net' in TEXT_parts:
                            try:
                                TEXT_parts = TEXT_parts.split('\n')[1]
                            except:
                                # url only
                                continue

                        results.append(data_format.get('message').format(**{
                            'DATE': DATE,
                            'TEXT': TEXT_parts,
                            'USER': USER,
                        }))

            if msg.get('filesharing'):
                files = msg.get('filesharing')
                for file in files:
                    if 'image/png' in file.get('mime'):
                        name = file.get('name')
                        src = f'{BASE_DIR}/{settings.directory}/{folder}/files/{name}'

                        time_ = datetime.fromtimestamp(msg.get('time')).strftime('%Y-%m-%d-%H-%M-%S')
                        new_name = f'0000000{IMG_COUNT}-PHOTO-{time_}.jpg'
                        IMG_COUNT += 1

                        dst = f'{settings.directory}/{folder}/{new_name}'

                        TEXT = file.get('caption')

                        if os.path.isfile(src):
                            im = Image.open(src)
                            rgb_im = im.convert('RGB')
                            rgb_im.save(dst)

                            results.append(data_format.get('file').format(**{
                                'DATE': DATE,
                                'FILE_NAME': new_name,
                                'USER': USER,
                            }))

                    if TEXT:
                        if TEXT_parts:
                            if TEXT == TEXT_parts:
                                continue

                        DATE_caption = datetime.fromtimestamp(msg.get('time')) + timedelta(seconds=1)
                        results.append(data_format.get('message').format(**{
                            'DATE': DATE_caption.strftime('%d.%m.%Y, %H:%M:%S'),
                            'TEXT': TEXT,
                            'USER': USER,
                        }))
            else:
                if TEXT:
                    results.append(data_format.get('message').format(**{
                        'DATE': DATE,
                        'TEXT': TEXT,
                        'USER': USER,
                    }))

    # замена id на имена при обращении в сообщениях
    results = replaceId(members_map, results)

    with open(f'{dst_folder}/_chat.txt', 'w+', encoding='utf-8') as f:
        f.write('\n'.join(list(reversed(results))))

    zipAndDel(dst_folder)
    return


def parseChat(folder: str, ME: str):
    results = []
    # ME = 'Константин Ковырзин'
    PERSON = ' '.join(folder.split('_'))

    files = os.listdir(f'{BASE_DIR}/results/{folder}/json/')
    map = {}
    IMG_COUNT = 3

    src_folder = createFolders(folder)

    for file in files:
        map.update({str(re.search(r'data_(\d+).json', file).group(1)): file})

    for i in tqdm(range(1, len(files))):
        file = map.get(str(i))
        # print(file)

        with open(f'{BASE_DIR}/results/{folder}/json/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for msg in data:
            DATE = datetime.fromtimestamp(msg.get('time')).strftime('%d.%m.%Y, %H:%M:%S')
            TEXT = msg.get('text')

            if msg.get('outgoing'):
                USER = ME
            else:
                USER = PERSON

            if msg.get('filesharing'):
                files = msg.get('filesharing')
                for file in files:
                    if 'image/png' in file.get('mime'):
                        name = file.get('name')
                        src = f'{BASE_DIR}/{settings.directory}/{folder}/files/{name}'

                        time_ = datetime.fromtimestamp(msg.get('time')).strftime('%Y-%m-%d-%H-%M-%S')
                        new_name = f'0000000{IMG_COUNT}-PHOTO-{time_}.jpg'
                        IMG_COUNT += 1

                        dst = f'{settings.directory}/{folder}/{new_name}'

                        TEXT = file.get('caption', '')

                        if os.path.isfile(src):
                            im = Image.open(src)
                            rgb_im = im.convert('RGB')
                            rgb_im.save(dst)

                            results.append(data_format.get('file').format(**{
                                'DATE': DATE,
                                'FILE_NAME': new_name,
                                'USER': USER,
                            }))

                    if TEXT:
                        DATE_caption = datetime.fromtimestamp(msg.get('time')) + timedelta(seconds=1)
                        results.append(data_format.get('message').format(**{
                            'DATE': DATE_caption.strftime('%d.%m.%Y, %H:%M:%S'),
                            'TEXT': TEXT,
                            'USER': USER,
                        }))
            else:
                results.append(data_format.get('message').format(**{
                    'DATE': DATE,
                    'TEXT': TEXT,
                    'USER': USER,
                }))

    with open(f'{src_folder}/_chat.txt', 'w+', encoding='utf-8') as f:
        f.write('\n'.join(list(reversed(results))))
    zipAndDel(src_folder)
    return


def zipAndDel(folder: str):
    name = folder.split('/')[-1]
    print('Архивация чата')
    shutil.make_archive(f'results/WhatsApp Chat - {name}', 'zip', folder)
    print('Удаление временной папки')
    shutil.rmtree(folder)


def replaceId(members_map: dict, results: list) -> list:
    data = []
    for res in results:
        persons = re.findall(r'@\[(\d+)]', res, re.DOTALL)
        if persons:
            for user_id in persons:
                user_name = members_map.get(user_id, {}).get('friendly')
                if user_name:
                    res: str = res.replace(user_id, user_name)

        data.append(res)

    return data


if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent.parent
    data_format = {
        'file': '[{DATE}] ~ {USER}: ‎<прикреплено: {FILE_NAME}>',
        'message': '[{DATE}] ~ {USER}: {TEXT}',  # 21.10.2020, 10:01:22
    }

    f_name = input(f'Введите название папки с чатом : ')
    chat_type = input(f'Выберете тип чата 1 - групповой, 2 - личный : ')

    if chat_type == '1':
        parseGroup(f_name)
    elif chat_type == '2':
        ME = input(f'Введите cвое имя : ')
        parseChat(f_name, ME)
    else:
        print(f'Неверный ввод типа чата {chat_type}')
