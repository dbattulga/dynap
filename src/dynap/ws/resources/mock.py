import logging
import socket
from flask_restful import Resource
from dynap.dao.collector import DaoCollector

logger = logging.getLogger("dynap.ws.resources.mock")


class MockInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (MockInterface, "", (dao_collector, )),
        ]


class MockInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self):
        logger.info("Calling Mock endpoint.")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # doesn't even have to be reachable
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except Exception:
                IP = '127.0.0.1'
            finally:
                s.close()
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the request."
                   }, 500
        return {"message": f"{IP}"}, 200
