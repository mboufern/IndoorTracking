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
import threading
from scapy.all import *

from rich.console import Console
from rich.prompt import Prompt


def parse_csv_line(line):
    # Parse a single line of airodump-ng CSV output and return a dict
    row = re.split(r'\s+', line.strip())
    if len(row) > 3:
        if len(row[2]) >= 16:
            now = datetime.now()
            return {
                'SensorName': 0,
                'MAC': row[2].strip(),
                'PWR': row[3].strip(),
                'log_at': now.strftime('%Y-%m-%d %H:%M:%S'),
            }
    return None


def get_wifi_data(interface):
    # Run airodump-ng command and continuously capture output to a dictionary
    cmd = f'airodump-ng -w /tmp/dump --output-format csv --write-interval 1 {interface}'
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

#_______________________________________________________________________________

# def extract_signal_power(packet):
#     # Try to extract signal power from RadioTap layer
#     if RadioTap in packet:
#         return response_packet[RadioTap].dBm_AntSignal
#     return None

# def send_probe_request(mac_address):
#     interface = "wlan0"
#
#     probe_request = (
#         RadioTap()
#         / Dot11(type=0, subtype=4, addr1="ff:ff:ff:ff:ff:ff", addr2=mac_address, addr3="ff:ff:ff:ff:ff:ff")
#         / Dot11ProbeReq()
#         / Dot11Elt(ID="SSID", info="")
#     )
#
#     response = srp(probe_request, iface=interface, timeout=2, verbose=False)
#
#     if response:
#         _, received_packets = response
#         if received_packets:
#             print(received_packets[0][1].layers())
#             response_packet = received_packets[0][1]
#             signal_power = extract_signal_power(response_packet)
#             return signal_power
#
#     return None

# def monitor_signal_power():
#     global list
#     print("thread started ")
#     while True:
#         for item in list:
#             mac_address = item["MAC"]
#             signal_power = send_probe_request(mac_address)
#
#             if signal_power is not None:
#                 print(f"Signal power of {mac_address}: {signal_power} dBm")
#                 now = datetime.now()
#                 new_obj = {'SensorName': 0, 'MAC': mac_address,'PWR': signal_power,'log_at': now.strftime('%Y-%m-%d %H:%M:%S'),}
#                 try:
#                     response = requests.post(url, data = json.dumps([new_obj]), headers = {'Content-Type': 'application/json'})
#
#                     if response.status_code == 200:
#                         print('Request successful')
#                         print(response.text)
#                     else:
#                         print('Request failed')
#                         print('Status Code:', response.status_code)
#                         print('Response:', response.text)
#
#                 except requests.exceptions.RequestException as e:
#                     print('An error occurred:', e)
#             else:
#                 print(f"No response received for {mac_address}.")
#
#         time.sleep(sending_interval)

def send_fake_probe_requests():
    global list
    print("started")
    while(True):
        for mac_address in list:
            probe_request = (
                RadioTap() /
                Dot11(type=0, subtype=4, addr1="ff:ff:ff:ff:ff:ff", addr2=mac_address["MAC"], addr3="ff:ff:ff:ff:ff:ff") /
                Dot11ProbeReq() /
                Dot11Elt(ID="SSID", info="")
            )

            sendp(probe_request, iface='wlan0', verbose=False)
        time.sleep(1)

monitor_thread = threading.Thread(target=send_fake_probe_requests)

list = []
url = "http://192.168.56.1:8000/api/dataentry"

monitor_thread.start()

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

