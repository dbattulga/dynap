import json
import logging
import time

from flask import request
from flask_restful import Resource
from dynap.dao.collector import DaoCollector
from dynap.dao.common import DaoEntryNotFound
from dynap.manager.section import CriticalSectionManager
from dynap.model.job import DeployedJob
from dynap.model.section import CriticalSection
from dynap.model.update_stream import UpdateStream

logger = logging.getLogger("dynap.ws.resources.update_stream")


class UpdateInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (UpdateInterface, "", (dao_collector,))
        ]


class UpdateInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def post(self):
        logger.info(f"Updating the job stream address.")
        try:
            json_data: dict = json.loads(request.json)
            print(f"this is the json data received on update USDS request {json_data}")
            request_data = UpdateStream.from_repr(json_data)

            deployed_jobs = self._dao_collector.job_dao.list()
            for deployed_job in deployed_jobs:
                for upstream in deployed_job.upstream:
                    if upstream.topic == request_data.topic:
                        upstream.address = request_data.agent_address
                for downstream in deployed_job.downstream:
                    if downstream.topic == request_data.topic:
                        downstream.address = request_data.agent_address
                self._dao_collector.job_dao.update(deployed_job)

        except (ValueError, KeyError) as e:
            logger.debug("Could not parse provided job data.", exc_info=e)
            return {
                       "message": "Could not complete the request: the provided data is not complete."
                   }, 400
        except Exception as e:
            logger.exception("Could not parse provided job data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return {}, 202
