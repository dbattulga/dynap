from __future__ import absolute_import, annotations

import logging.config
import os

from dynap.common.logging import get_logging_configuration
from dynap.dao.collector import DaoCollectorBuilder
from dynap.ws.ws import WsInterface

logging.config.dictConfig(get_logging_configuration("dynap"))

logger = logging.getLogger("dynap.main")


def init_ws() -> WsInterface:
    #mongo_db_host = "localhost"
    mongo_db_host = os.getenv("MONGODB_HOST")
    mongo_db_port = 27017
    mongo_db_username = "admin"
    mongo_db_password = "admin"
    mongo_db_database = "dynap"

    dao_collector = DaoCollectorBuilder.mongo_db(
        mongo_db_host,
        mongo_db_port,
        mongo_db_username,
        mongo_db_password,
        mongo_db_database
    )

    ws_interface = WsInterface(dao_collector)
    return ws_interface


ws = init_ws()
flask_application = ws.get_application()

if __name__ == "__main__":
    ws.run_server(port=5001)

