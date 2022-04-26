import logging

from flask import request
from flask_restful import Resource
from dynap.dao.collector import DaoCollector

logger = logging.getLogger("dynap.ws.resources.mock")


class MockInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (MockInterface, "/<string:job_id>", (dao_collector, )),
        ]


class MockInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def post(self, job_id):
        logger.info("Calling Mock endpoint.")
        json_data: dict = request.json
        try:
            migration_address = json_data.get("migration_address")
            print(f"Migration address: {migration_address}")
            print(f"job_id: {job_id}")
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return {}, 200
