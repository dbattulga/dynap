from __future__ import absolute_import, annotations

import logging
import json
import requests
import os
from dynap.dao.collector import DaoCollector

logger = logging.getLogger("dynap.manager.flink")


class FlinkManager:

    def __init__(self, dao_collector: DaoCollector):
        self._dao_collector = dao_collector

    @staticmethod
    def upload_jar(base_url, jarpath):
        try:
            files = {"jarfile": (os.path.basename(jarpath), open(jarpath, "rb"), "application/x-java-archive")}
            upload = requests.post(base_url + "/jars/upload", files=files)
            response = json.loads(upload.content)
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the upload jar request."
                   }, 500
        return {"message": FlinkManager._get_upload_id(response["filename"])}, 200

    @staticmethod
    def _find_all(a_str, sub):
        start = 1
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub) # use start += 1 to find overlapping matches


    @staticmethod
    def _get_upload_id(str):
        lst = list(FlinkManager._find_all(str, '/'))
        return (str[lst[-1]+1:])


    @staticmethod
    def start_jar(base_url, jarid, entryclass, broker, sourcetopic, sinktopic, jobname):
        broker = broker
        sourcetopic = ','.join(sourcetopic)
        sinktopic = ','.join(sinktopic)
        programArgs = "--jobname '"+jobname+"' --broker '"+broker+"' --sourcetopic '"+sourcetopic+"' --sinktopic '"+sinktopic+"' "
        propertiess = {
            "entryClass": entryclass,
            "programArgs": programArgs
        }
        try:
            start = requests.post(base_url + "/jars/"+jarid+"/run", json=propertiess)
            response = json.loads(start.content)
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the start jar request."
                   }, 500
        return {"message": response["jobid"]}, 200


    @staticmethod
    def delete_jar(base_url, jarid):
        try:
            delete = requests.delete(base_url + "/jars/" +jarid)
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the delete request."
                   }, 500
        return {}, 200


    @staticmethod
    def terminate_job(base_url, jobid):
        try:
            stop = requests.patch(base_url + "/jobs/" + jobid)
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the stop job request."
                   }, 500
        return {}, 200


    @staticmethod
    def stop_job(base_url, jobid):
        try:
            stop = requests.post(base_url + "/jobs/" + jobid + "/stop")
        except Exception as e:
            logger.exception(f"Could not parse provided event data.", exc_info=e)
            return {
                       "message": "Something bad happened: could not complete the stop job request."
                   }, 500
        return {}, 200
