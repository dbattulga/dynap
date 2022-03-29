import json
import logging
import time

from flask import request
from flask_restful import Resource
from dynap.dao.collector import DaoCollector
from dynap.manager.section import CriticalSectionManager
from dynap.model.section import CriticalSection

logger = logging.getLogger("dynap.ws.resources.section")


class SectionInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (SectionInterface, "", (dao_collector,))
        ]


class SectionInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def post(self):
        logger.info(f"Requesting the critical section.")
        try:
            json_data: dict = json.loads(request.json)
            request_data = CriticalSection.from_repr(json_data)
            logger.info(f"Getting assiciated job.")
            job = CriticalSectionManager.get_associated_job(self._dao_collector, request_data.topic, request_data.job_name)
            logger.info(f"Got job by topic, requesting_cs is {job.requesting_cs}")
            jobid = job.job_id

            # update sequence number by received topic
            CriticalSectionManager.update_sequence_number(self._dao_collector, jobid, request_data.topic, request_data.sequence_number)

            # checking if job is in CS
            if job.requesting_cs:
                logger.info(f"Got job by id, job exists, entering CS check.")
                if job.sequence_number > request_data.sequence_number:
                    pass
                elif job.sequence_number == request_data.sequence_number:
                    if job.job_name > request_data.job_name:
                        pass
                    else:
                        while True:
                            time.sleep(1)
                            if not CriticalSectionManager.check_job_request_status(self._dao_collector, jobid):
                                break
                elif job.sequence_number < request_data.sequence_number:
                    while True:
                        time.sleep(1)
                        if not CriticalSectionManager.check_job_request_status(self._dao_collector, jobid):
                            break
            else:
                pass

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
