import logging

from flask_restful import Resource
from dynap.dao.collector import DaoCollector
from dynap.manager.metrics import MetricsManager

logger = logging.getLogger("dynap.ws.resources.task_slots")


class TaskSlotsInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (TaskSlotsInterface, "", (dao_collector, )),
        ]


class TaskSlotsInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self):
        logger.info("Checking on available task slot endpoint.")
        try:
            task_slots = MetricsManager.get_available_task_slots()
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {"slots_available": 0}, 500
        return {"slots_available": task_slots}, 200
