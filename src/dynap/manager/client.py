from __future__ import absolute_import, annotations

import logging
import paho.mqtt.client as mqtt
from dynap.dao.collector import DaoCollector
from dynap.model.client import Client

logger = logging.getLogger("dynap.manager.client")


class ClientManager:

    def __init__(self, dao_collector: DaoCollector):
        self._dao_collector = dao_collector

    @staticmethod
    def on_message(client: mqtt.Client, userdata: Client, message):
        pub_client = mqtt.Client(userdata.client_id, clean_session=False)
        pub_client.connect(userdata.sink_address)
        pub_client.publish(topic=userdata.topic, payload=str(message.payload.decode("utf-8")), qos=1, retain=False)
        #pub_client.disconnect()
        msg = str(message.payload.decode("utf-8"))
        logger.info(f"Client on message {msg}")

    @staticmethod
    def on_connect(client: mqtt.Client, userdata: Client, flags, rc):
        if rc == 0:
            client.connected_flag = True
        else:
            logger.info(f"Bad connection returned, Rode {rc}")
            client.loop_stop()

    @staticmethod
    def on_disconnect(client: mqtt.Client, userdata, rc):
        logger.info(f"Client {client} disconnected ok")
        client.loop_stop()

