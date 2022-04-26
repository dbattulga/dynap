import json
import logging
import os

import requests
from flask import request
from flask_restful import Resource
from dynap.dao.collector import DaoCollector
from dynap.manager.section import CriticalSectionManager
from dynap.model.client import Client
from dynap.model.common import Common
from dynap.model.job import Job
from dynap.model.section import CriticalSection
from dynap.model.update_stream import UpdateStream

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
            job = self._dao_collector.job_dao.get(job_id)

            # SET OUR JOB AS ENTERING CS
            job.requesting_cs = True
            self._dao_collector.job_dao.update(job)

            # GET OUR SEQUENCE NUMBER
            our_sequence_number = CriticalSectionManager.get_max_sequence_number(self._dao_collector, job.job_name)
            our_sequence_number += 1
            job.sequence_number = our_sequence_number

            # REQUESTING CS FROM DS AND US
            for upstream in job.upstream:
                cs_upstream = CriticalSection(
                    job_name=job.job_name,
                    agent_address=job.agent_address,
                    sequence_number=our_sequence_number,
                    topic=upstream.topic
                )
                logger.debug(f"Requesting CS from upstream [{upstream.topic}].")
                req = requests.post(Common.HTTP + upstream.address + Common.AGENT_PORT + "/section", json=json.dumps(cs_upstream.to_repr()))
                print(req)

            for downstream in job.downstream:
                cs_downstream = CriticalSection(
                    job_name=job.job_name,
                    agent_address=job.agent_address,
                    sequence_number=our_sequence_number,
                    topic=downstream.topic
                )
                logger.debug(f"Requesting CS from downstream [{downstream.topic}].")
                req = requests.post(Common.HTTP + downstream.address + Common.AGENT_PORT + "/section", json=json.dumps(cs_downstream.to_repr()))
                print(req)

            # START OF THE ACTUAL MIGRATION
            # DELETE US DS FORWARDERS AND STOP OUR JOB
            for upstream in job.upstream:
                client_id = Client.build_name(upstream.topic)
                requests.delete(Common.HTTP + upstream.address + Common.AGENT_PORT + "/client/" + client_id)

            requests.delete(Common.HTTP + job.agent_address + Common.AGENT_PORT + "/job/" + job.job_id)
            file_path = Common.JOB_PATH + "/" + job.jar_name

            for downstream in job.downstream:
                client_id = Client.build_name(downstream.topic)
                requests.delete(Common.HTTP + job.agent_address + Common.AGENT_PORT + "/client/" + client_id)

            # PREPARE THE MIGRATION REQUEST
            data = Job.to_repr(job)
            data["agent_address"] = migration_address
            url = Common.HTTP + migration_address + Common.AGENT_PORT + "/job"
            files = [
                ('file', (job.jar_name, open(file_path, 'rb'), 'application/java-archive'))
            ]
            req = requests.post(url, files=files, data={"data": json.dumps(data)})
            print(req)
            os.remove(file_path)

            # REDIRECTING US/DS WITH MIGRATING ADDRESS
            for downstream in job.downstream:
                update_data_ds = UpdateStream(
                    agent_address=migration_address,
                    topic=downstream.topic
                )
                req = requests.post(Common.HTTP + downstream.address + Common.AGENT_PORT + "/update", json=json.dumps(update_data_ds.to_repr()))
                print(req)
            for upstream in job.upstream:
                update_data_us = UpdateStream(
                    agent_address=migration_address,
                    topic=upstream.topic
                )
                req = requests.post(Common.HTTP + upstream.address + Common.AGENT_PORT + "/update", json=json.dumps(update_data_us.to_repr()))
                print(req)

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
