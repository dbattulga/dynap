from __future__ import absolute_import, annotations

import logging
import yaml
import json
import requests
import datetime as dt
import asyncio

from aiohttp import ClientSession, FormData

logger = logging.getLogger("dynap.deployer.deploy")


def run_conf():
    with open('pipeline.yml') as f:
        userconf = yaml.safe_load(f)
    userjobs = []

    for userjob in userconf['jobs']:
        userjobs.append(userjob['job_name'])
        url = 'http://' + userjob['agent_address'] + ":5001/job"
        print(f"posting: {userjob['job_name']} on {url}")

        data = {
            "job_name": userjob['job_name'],
            "agent_address": userjob['agent_address'],
            "upstream": [],
            "downstream": [],
            "entry_class": userjob['entry_class'],
            "sequence_number": userjob['sequence_number']
        }
        for i in range(len(userjob['upstream_broker'])):
            upstream = {
                "address": userjob['upstream_broker'][i],
                "topic": userjob['upstream_topic'][i],
                "sequence_number": 0,
                "requesting_cs": False
            }
            data["upstream"].append(upstream)
        for i in range(len(userjob['downstream_broker'])):
            downstream = {
                "address": userjob['downstream_broker'][i],
                "topic": userjob['downstream_topic'][i],
                "sequence_number": 0,
                "requesting_cs": False
            }
            data["downstream"].append(downstream)

        files = [
            ('file', ('test.jar', open(userjob["job_path"], 'rb'), 'application/java-archive'))
        ]
        req = requests.post(url, files=files, data={"data": json.dumps(data)})

        print(data)
        print(req)


# with open('pipeline.yml') as f:
#     userconf = yaml.safe_load(f)
# userjobs = []
#
#
# async def run_conff():
#     async with ClientSession() as session:
#         for userjob in userconf['jobs']:
#             print(userjob['job_name'])
#             userjobs.append(userjob['job_name'])
#             url = 'http://' + userjob['agent_address'] + ":5001/job"
#             print(f"posting: {userjob['job_name']} on {url}")
#
#             data = {
#                 "job_name": userjob['job_name'],
#                 "agent_address": userjob['agent_address'],
#                 "upstream": [],
#                 "downstream": [],
#                 "entry_class": userjob['entry_class']
#             }
#             for i in range(len(userjob['upstream_broker'])):
#                 upstream = {
#                     "address": userjob['upstream_broker'][i],
#                     "topic": userjob['upstream_topic'][i]
#                 }
#                 data["upstream"].append(upstream)
#             for i in range(len(userjob['downstream_broker'])):
#                 downstream = {
#                     "address": userjob['downstream_broker'][i],
#                     "topic": userjob['downstream_topic'][i]
#                 }
#                 data["downstream"].append(downstream)
#
#             dada = FormData()
#             dada.add_field(
#                 name='file',
#                 value=open(userjob["job_path"], 'rb'),
#                 filename='test.jar',
#                 content_type='application/java-archive')
#             dada.add_field(
#                 name='data',
#                 value=json.dumps(data)
#             )
#
#         async with session.post(url, data=dada) as response:
#             response = await response.read()
#             print(response)
#         await asyncio.sleep(1)
#         print(data)
#
#
# async def something():
#     await asyncio.gather(run_conff())

n1=dt.datetime.now()
# asyncio.run(something())
run_conf()
n2=dt.datetime.now()
print(n2-n1)