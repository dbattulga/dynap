from __future__ import absolute_import, annotations

import os
from dataclasses import dataclass

import logging
logger = logging.getLogger("dynap.model")


@dataclass
class Common:
    HTTP = "http://"
    MQTT_PORT = ":1883"
    FLINK_PORT = ":8081"
    AGENT_PORT = ":5001"
    JOB_PATH = os.getenv("JOB_PATH")
    BASE_URL = "localhost"
