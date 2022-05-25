#! /usr/bin/env python

import json
import os
import requests
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlparse

from banyan.api import BanyanApiClient
from banyan.api.event_v2 import EventV2

bc = BanyanApiClient()
api_url = urlparse(bc.api_url)
api_host = api_url.hostname.split('.')[0]

sumo_webhook = os.getenv('SUMO_WEBHOOK')
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

end_dt = datetime.now()
start_dt = end_dt - timedelta(minutes=10)

# Save events to this file as multiline JSON for Sumo ingest
file_path = "/tmp/log_file"

events: List[EventV2] = bc.events.list(before_dt=end_dt, after_dt=start_dt)
print(f'Found {len(events)} events from {start_dt} to {end_dt}')

def lambda_handler(event, context):
    with open(file_path, "a", encoding='utf-8') as f:
        for e in events:
            # convert event back to JSON
            message = EventV2.Schema().dump(e)
            
            # capture source/destination IP:host info
            if e.link is not None:
                message['network'] = {}
                if e.link.source.host_name != '':
                    ip, port = e.link.source.host_name.split(':')
                    message['network']['client'] = {'ip': ip, 'port': int(port)}
                elif e.link.source.ip != '':
                    ip, port = e.link.source.ip.split(':')
                    message['network']['client'] = {'ip': ip, 'port': int(port)}
                if e.link.destination.host_name != '':
                    ip, port = e.link.destination.host_name.split(':')
                    message['network']['destination'] = {'ip': ip, 'port': int(port)}
                elif e.link.destination.ip != '':
                    ip, port = e.link.destination.ip.split(':')
                    message['network']['destination'] = {'ip': ip, 'port': int(port)}
            
            # remove empty blocks
            if 'policy' in message and message['policy']['name'] == '':
                del message['policy']
            if 'trustscore' in message and message['trustscore']['timestamp'] == 0:
                del message['trustscore']
            
            # convert created_at timestamp to timezone-aware ISO format
            created_at = e.created_at.astimezone()
            message['timestamp'] = created_at.isoformat()
            
            item = json.dumps(message)
            # append each item to the file
            f.write(item+"\n")
    logs = open(file_path, 'rb').read()
    response = requests.post(sumo_webhook, headers=headers, data=logs)
    print(response)
    os.remove(f.name)


