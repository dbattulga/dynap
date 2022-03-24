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
            json_data: dict = request.json
            request_data = CriticalSection.from_repr(json_data)
            job = CriticalSectionManager.get_associated_job(self._dao_collector, request_data.topic)
            jobid = job.job_id

            if CriticalSectionManager.check_job_exist(self._dao_collector, jobid):
                if job.requesting_cs:
                    if job.sequence_number > request_data.sequence_number:
                        pass
                    elif job.sequence_number == request_data.sequence_number:
                        if job.job_name > request_data.job_name:
                            pass
                        else:
                            while True:
                                time.sleep(1)
                                if not CriticalSectionManager.check_job_exist(self._dao_collector, jobid):
                                    break
                    elif job.sequence_number < request_data.sequence_number:
                        while True:
                            time.sleep(1)
                            if not CriticalSectionManager.check_job_exist(self._dao_collector, jobid):
                                break
                else:
                    pass
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
