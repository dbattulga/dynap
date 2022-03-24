import json
import logging
import os
import uuid

import requests
from flask import request
from flask_restful import Resource, abort
from dynap.dao.collector import DaoCollector
from dynap.dao.common import DaoEntryNotFound
from dynap.manager.flink import FlinkManager
from dynap.model.client import Client
from dynap.model.common import Common
from dynap.model.job import Job, DeployedJob

logger = logging.getLogger("dynap.ws.resources.job")


class JobInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (JobInterface, "", (dao_collector,)),
            (JobInterfaceId, "/<string:job_id>", (dao_collector,))
        ]


class JobInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self):
        logger.info("Listing jobs.")
        deployed_jobs = self._dao_collector.job_dao.list()
        return [job.to_repr() for job in deployed_jobs], 200

    def post(self):
        logger.info("Creating new job.")
        try:
            uploaded_file = request.files.get('file')
            json_data = json.loads(request.form.get('data'))
            job = Job.from_repr(json_data)
            filename = str(uuid.uuid4()) + '.jar'
            source_topic = []
            sink_topic = []
            for upstream in job.upstream:
                source_topic.append(upstream.topic)
                json_data = {
                    "client_id": Client.build_name(upstream.topic),
                    "agent_address": upstream.address,
                    "topic": upstream.topic,
                    "sink_address": job.agent_address
                }
                if upstream.address != job.agent_address:
                    requests.post(Common.HTTP + upstream.address + Common.AGENT_PORT + "/client", json=json_data)

            for downstream in job.downstream:
                sink_topic.append(downstream.topic)
                json_data = {
                    "client_id": Client.build_name(downstream.topic),
                    "agent_address": job.agent_address,
                    "topic": downstream.topic,
                    "sink_address": downstream.address
                }
                if downstream.address != job.agent_address:
                    requests.post(Common.HTTP + job.agent_address + Common.AGENT_PORT + "/client", json=json_data)

            uploaded_file.save(os.path.join(Common.JOB_PATH, filename))
            spe_address = Common.HTTP + job.agent_address + Common.FLINK_PORT
            file_path = Common.JOB_PATH + "/" + filename

            jar_upload_response = FlinkManager.upload_jar(spe_address, file_path)
            if jar_upload_response[1] == 200:
                jar_id = jar_upload_response[0]["message"]
                jar_start_response = FlinkManager.start_jar(
                    base_url=spe_address,
                    jarid=jar_id,
                    entryclass=job.entry_class,
                    broker=job.agent_address,
                    sourcetopic=source_topic,
                    sinktopic=sink_topic,
                    jobname=job.job_name)
                if jar_start_response[1] == 200:
                    job_id = jar_start_response[0]["message"]
                else:
                    raise Exception("Jar not successfully started.")
            else:
                raise Exception("Jar not successfully uploaded.")

            deployed_job = DeployedJob(
                    job_name=job.job_name,
                    agent_address=job.agent_address,
                    upstream=job.upstream,
                    downstream=job.downstream,
                    entry_class=job.entry_class,
                    sequence_number=job.sequence_number,
                    jar_id=jar_id,
                    job_id=job_id,
                    jar_name=filename,
                    requesting_cs=False
                )
            self._dao_collector.job_dao.save(deployed_job)
        except Exception as e:
            logger.exception("Could not parse provided data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return deployed_job.to_repr(), 201


class JobInterfaceId(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self, job_id):
        logger.info(f"Getting details of the job [{job_id}]")
        try:
            job = self._dao_collector.job_dao.get(job_id)
        except DaoEntryNotFound:
            abort(404, message=f"Job with id [{job_id}] not found")
            return
        except Exception as e:
            logger.exception(f"Provided id [{job_id}] is not valid.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return job.to_repr(), 200

    def put(self, job_id):
        logger.info(f"Updating the job [{job_id}]")
        json_data: dict = request.json

        try:
            job = DeployedJob.from_repr(json_data)
            self._dao_collector.job_dao.update(job)
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
        return job.to_repr(), 202

    def delete(self, job_id):
        logger.info(f"Deleting the job [{job_id}]")
        try:
            job = self._dao_collector.job_dao.get(job_id)
            spe_address = Common.HTTP + job.agent_address + Common.FLINK_PORT
            file_path = Common.JOB_PATH + "/" + job.jar_name
            # os.remove(file_path)
            delete_jar_request = FlinkManager.delete_jar(spe_address, job.jar_id)
            if delete_jar_request[1] == 200:
                stop_job_request = FlinkManager.terminate_job(spe_address, job_id)
                if stop_job_request[1] == 200:
                    self._dao_collector.job_dao.delete(job_id)
                else:
                    raise Exception("Job not successfully stopped.")
            else:
                raise Exception("Jar not successfully deleted.")

        except Exception as e:
            logger.exception("Could not parse provided data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return {}, 200
