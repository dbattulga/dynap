import logging

from flask import request
from flask_restful import Resource, abort
import paho.mqtt.client as mqtt

from dynap.dao.collector import DaoCollector
from dynap.dao.common import DaoEntryNotFound
from dynap.manager.client import ClientManager
from dynap.model.client import Client

logger = logging.getLogger("dynap.ws.resources.client")


class ClientInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (ClientInterface, "", (dao_collector, )),
            (ClientInterfaceId, "/<string:client_id>", (dao_collector, ))
        ]


class ClientInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self):
        logger.info("Listing clients.")
        try:
            results = self._dao_collector.client_dao.list()
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return [client.to_repr() for client in results], 200

    def post(self):
        logger.info("Creating new mqtt client.")
        json_data: dict = request.json
        try:
            mqtt_client = Client.from_repr(json_data)
            try:
                self._dao_collector.client_dao.get(mqtt_client.client_id)
                return {
                           "message": f"Client with id [{mqtt_client.client_id}] is already present"
                       }, 404
            except DaoEntryNotFound:
                client = mqtt.Client(mqtt_client.client_id, userdata=mqtt_client, clean_session=False)
                client.connect(mqtt_client.agent_address)
                client.subscribe(mqtt_client.topic, qos=1)
                client.on_connect = ClientManager.on_connect
                client.on_message = ClientManager.on_message
                client.on_disconnect = ClientManager.on_disconnect
                client.loop_start()
                self._dao_collector.client_dao.save(mqtt_client)
        except (ValueError, KeyError) as e:
            logger.debug(f"Could not parse provided client data.", exc_info=e)
            return {
                       "message": "Could not complete the request: the provided data is not complete."
                   }, 400
        except Exception as e:
            logger.exception(f"Could not parse provided client data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return mqtt_client.to_repr(), 201


class ClientInterfaceId(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self, client_id):
        logger.info(f"Getting details for mqtt client [{client_id}]")
        try:
            client = self._dao_collector.client_dao.get(client_id)
        except DaoEntryNotFound:
            abort(404, message=f"Client with id [{client_id}] not found")
            return
        except Exception as e:
            logger.exception(f"Provided id [{client_id}] is not valid.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return client.to_repr(), 200

    # def put(self, client_id):
    #     logger.info(f"Updating the mqtt client [{client_id}]")
    #     json_data: dict = request.json
    #     try:
    #         client = Client.from_repr(json_data)
    #         self._dao_collector.client_dao.update(client)
    #     except (ValueError, KeyError) as e:
    #         logger.debug(f"Could not parse provided client data.", exc_info=e)
    #         return {
    #                    "message": "Could not complete the request: the provided data is not complete."
    #                }, 400
    #     except Exception as e:
    #         logger.exception(f"Could not parse provided client data.", exc_info=e)
    #         return {
    #                    "message": "Something bad happened: could not complete the request."
    #                }, 500
    #     return client.to_repr(), 202

    def delete(self, client_id):
        logger.info(f"Deleting the mqtt client [{client_id}]")
        client = mqtt.Client(client_id, clean_session=False)
        # mqtt_client = self._dao_collector.client_dao.get(client_id)
        client.disconnect()
        # client.connect(mqtt_client.agent_address)
        # client.on_disconnect = ClientManager.on_disconnect
        # client.loop_stop()
        self._dao_collector.client_dao.delete(client_id)
        return {}, 200
