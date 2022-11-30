import random
import string
from time import sleep
import requests
import sys
from requests_toolbelt import MultipartEncoder

url = 'https://themis.ii.uni.wroc.pl/'
host = 'themis.ii.uni.wroc.pl'


def auth(login, passwd):
    response = requests.post(url + 'login', data={'userid': login, 'passwd': passwd},
                             headers={'Host': host, 'Referer': 'https://themis.ii.uni.wroc.pl/'})
    return response.request.headers['Cookie']


def find_type(entry: str):
    types = ['overseer', 'admin', 'user']

    return any([entry.split('>')[1].split('<')[0].find(i, 0, 15) != -1 for i in types])


def extract_group(entry: str):
    return entry.split('href=')[1].split('"')[1]


def get_groups(text: str):
    return map(extract_group, filter(find_type, text.split('<div class="section-type')))


def print_groups(cookies: str):
    response = requests.get(url, headers={'Host': host, 'Cookie': cookies})
    for entry in get_groups(response.text):
        print(entry)


def get_tasks(text: str) -> list[str]:
    list_of_tasks = []
    while True:
        found = text.find('problem-code')
        if found == -1:
            break
        t = text[found + 13:found + 100].split('>')[2].split('<')[0]
        text = text[found + 13:]
        list_of_tasks.append(t)
    return list_of_tasks


def print_tasks(cookies: str, group: str):
    response = requests.get(url + group, headers={'Host': host, 'Cookie': cookies})
    lst = get_tasks(response.text)

    for i in lst:
        print('\"{}\"'.format(i))


def print_results(text: str):
    text = text.split('<tr>')
    text = text[2:]
    idx = 1
    emotes = []
    for i in text:
        t = i.split('<td>')
        if t[8].split('>')[1].split('<')[0] == 'accepted':
            print('{}. {}     {}/{}'.format(idx, t[8].split('>')[1].split('<')[0], t[3].split('<')[0],
                                            t[4].split('<')[0]))
            emotes.append('✅')
        else:
            print('{}. {}'.format(idx, t[8].split('>')[1].split('<')[0]))
            emotes.append('❌')
        idx += 1
    print(''.join(emotes))


def sumbit(cookies: str, group: str, task: str, filename: str):
    languages = {
        'cpp': 'g++',
        'c': 'gcc',
        'RAM': 'ram'
    }

    with open(filename, 'r') as f:
        code = f.read()

    fields = {
        'source': code,
        'file': '',
        'lang': languages[filename.split('.')[-1]]
    }

    boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
    m = MultipartEncoder(fields=fields, boundary=boundary)

    headers = {
        "Host": host,
        "Cookie": cookies,
        "Connection": "keep-alive",
        "Content-Type": m.content_type,
        "Referer": url + group + '/' + task
    }

    response = requests.post(url + group + "/" + task + "/submit", headers=headers, data=m)
    ret_code = response.text

    headers2 = {
        "Host": "themis.ii.uni.wroc.pl",
        "Cookie": cookies,
        "Connection": "keep-alive",
        "Referer": url + group + '/' + task
    }

    print('Submitting...')
    while True:
        sleep(0.25)
        response = requests.get(url + group + "/result/" + ret_code, headers=headers2)
        if response.text.find('compiling') == -1 and response.text.find('running') == -1 and response.text.find(
                'waiting') == -1:
            break

    print_results(response.text)



help_message = '''
Welcome to The themis submitter
Options:
'list groups' - listing groups
'list tasks <group_name>' - listing tasks in given groupname
'submit <group_name> <task_name> <path_to_src>' - submiting code and prinitng results
ver. 2.71828182...
'''
