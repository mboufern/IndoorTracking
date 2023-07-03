# import pyrcrack
# import asyncio
import subprocess
import csv
import time
import io
import re
import json
import datetime
import requests
from urllib3 import PoolManager

from rich.console import Console
from rich.prompt import Prompt


def parse_csv_line(line):
    # Parse a single line of airodump-ng CSV output and return a dict
    row = re.split(r'\s+', line.strip())
    if len(row) > 3:
        if len(row[2]) >= 16:
            now = datetime.datetime.now()
            return {
                'SensorName': 0,
                'MAC': row[2].strip(),
                'PWR': row[3].strip(),
                'log_at': now.strftime('%Y-%m-%d %H:%M:%S'),
            }
    return None


def get_wifi_data(interface):
    # Run airodump-ng command and continuously capture output to a dictionary
    cmd = f'airodump-ng -w /tmp/dump --output-format csv --ivs {interface}'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    csvreader = csv.reader(io.TextIOWrapper(proc.stdout), delimiter=',')

    while True:
        # Read the next line of CSV output
        try:
            line = next(csvreader)
        except StopIteration:
            break

        data = parse_csv_line(','.join(line))

        # Yield the data to the caller
        if data != None:
            # check if the device was already scanned, if yes check if his power has changed(remove the existing one and replace it with the new one). if not add the new device to the list
            exist = False
            for l in list:
                if data['MAC'] == l['MAC'] and data['PWR'] == l['PWR']:
                    exist = True
                    break
                elif data['MAC'] == l['MAC']:
                    list.remove(l)
                    break

            if exist == False:
                subprocess.call(["kill", "-SIGINT", str(proc.pid)])
                yield data

    # Kill the airodump-ng process
    proc.kill()

url = "http://192.168.56.1:8000/api/dataentry"

# int_address = ('192.168.56.101', 0)
# pool_manager = PoolManager(source_address = int_address)

list = []
for data in get_wifi_data('wlan0'):
    print(data)
    list.append(data)
    try:
        response = requests.post(url, data = json.dumps(data), headers = {'Content-Type': 'application/json'})

        if response.status_code == 200:
            print('Request successful')
            print(response.text)
        else:
            print('Request failed')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)

