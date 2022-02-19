from __future__ import absolute_import, annotations

import logging
import yaml
import json
import requests
import datetime as dt

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
            "entry_class": userjob['entry_class']
        }
        for i in range(len(userjob['upstream_broker'])):
            upstream = {
                "address": userjob['upstream_broker'][i],
                "topic": userjob['upstream_topic'][i]
            }
            data["upstream"].append(upstream)
        for i in range(len(userjob['downstream_broker'])):
            downstream = {
                "address": userjob['downstream_broker'][i],
                "topic": userjob['downstream_topic'][i]
            }
            data["downstream"].append(downstream)

        files = [
            ('file', ('test.jar', open(userjob["job_path"], 'rb'), 'application/java-archive'))
        ]
        req = requests.post(url, files=files, data={"data": json.dumps(data)})

        print(data)
        print(req)


n1=dt.datetime.now()
run_conf()
n2=dt.datetime.now()
print(n2-n1)