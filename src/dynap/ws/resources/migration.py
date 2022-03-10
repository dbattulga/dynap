import json
import logging
import os

import requests
from flask import request
from flask_restful import Resource
from dynap.dao.collector import DaoCollector
from dynap.model.client import Client
from dynap.model.common import Common
from dynap.model.job import Job

logger = logging.getLogger("dynap.ws.resources.migration")


class MigrationInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (MigrationInterface, "/<string:job_id>", (dao_collector,))
        ]

class MigrationInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def post(self, job_id):
        logger.info(f"Migrating the job [{job_id}].")
        json_data: dict = request.json

        try:
            migration_address = json_data.get("migration_address")
            # TODO mutex endpoint will trigger here
            job = self._dao_collector.job_dao.get(job_id)
            for upstream in job.upstream:
                client_id = Client.build_name(upstream.topic)
                requests.delete(Common.HTTP + upstream.address + Common.AGENT_PORT + "/client/" + client_id)

            requests.delete(Common.HTTP + job.agent_address + Common.AGENT_PORT + "/job/" + job.job_id)
            file_path = Common.JOB_PATH + "/" + job.jar_name

            for downstream in job.downstream:
                client_id = Client.build_name(downstream.topic)
                requests.delete(Common.HTTP + job.agent_address + Common.AGENT_PORT + "/client/" + client_id)

            data = Job.to_repr(job)
            data["agent_address"] = migration_address
            url = Common.HTTP + migration_address + Common.AGENT_PORT + "/job"
            files = [
                ('file', (job.jar_name, open(file_path, 'rb'), 'application/java-archive'))
            ]
            req = requests.post(url, files=files, data={"data": json.dumps(data)})
            print(req)

            os.remove(file_path)
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
        return {}, 201
