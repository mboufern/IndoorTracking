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

from rich.console import Console
from rich.prompt import Prompt


def parse_csv_line(line):
    # Parse a single line of airodump-ng CSV output and return a dict
    row = re.split(r'\s+', line.strip())
    if len(row) > 3:
        if len(row[2]) >= 16:
            now = datetime.datetime.now()
            return {
                'sensor_id': '1',
                'MAC': row[2].strip(),
                'pwr': row[3].strip(),
                'TIME': now.strftime('%Y-%m-%d %H:%M:%S'),
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
                if data['MAC'] == l['MAC'] and data['pwr'] == l['pwr']:
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

url = "http://127.0.0.1:8000/api/data_entry"
list = []
for data in get_wifi_data('wlan0'):
    print(data)
    list.append(data)
    # requests.post(url, json = data)

