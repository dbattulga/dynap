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


class VisualizerInterfaceBuilder:

    @staticmethod
    def routes(dao_collector: DaoCollector):
        return [
            (VisualizerInterface, "", (dao_collector,))
        ]

class VisualizerInterface(Resource):

    def __init__(self, dao_collector: DaoCollector) -> None:
        super().__init__()
        self._dao_collector = dao_collector

    def get(self):
        pass
