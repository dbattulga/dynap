from __future__ import absolute_import, annotations

from flask import Flask
from flask_restful import Api

import logging

from dynap.dao.collector import DaoCollector
from dynap.model.common import Common
from dynap.ws.resources.job import JobInterfaceBuilder
from dynap.ws.resources.client import ClientInterfaceBuilder
from dynap.ws.resources.migration import MigrationInterfaceBuilder
from dynap.ws.resources.section import SectionInterfaceBuilder
from dynap.ws.resources.update_stream import UpdateInterfaceBuilder

logger = logging.getLogger("dynap.ws.ws")


class WsInterface:

    def __init__(self, dao_collector: DaoCollector) -> None:
        self._app = Flask("api")
        self._api = Api(app=self._app)
        self._init_modules(dao_collector)
        self._app.config["UPLOAD_FOLDER"] = Common.JOB_PATH

    def _init_modules(self, dao_collector: DaoCollector) -> None:
        active_routes = [
            (JobInterfaceBuilder.routes(dao_collector), "/job"),
            (ClientInterfaceBuilder.routes(dao_collector), "/client"),
            (MigrationInterfaceBuilder.routes(dao_collector), "/migrate"),
            (SectionInterfaceBuilder.routes(dao_collector), "/section"),
            (UpdateInterfaceBuilder.routes(dao_collector), "/update")
        ]

        for module_routes, prefix in active_routes:
            for resource, path, args in module_routes:
                logger.debug("Installing route %s", prefix + path)
                self._api.add_resource(resource, prefix + path, resource_class_args=args)

    def run_server(self, host: str = "0.0.0.0", port: int = 80, debug=False):
        self._app.run(host=host, port=port, debug=debug)

    def get_application(self):
        return self._app

    @property
    def app(self):
        return self._app
