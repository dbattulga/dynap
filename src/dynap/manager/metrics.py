from __future__ import absolute_import, annotations

import logging
import requests
from dynap.dao.collector import DaoCollector

logger = logging.getLogger("dynap.model")


class MetricsManager:

    def __init__(self, dao_collector: DaoCollector):
        self._dao_collector = dao_collector

    @staticmethod
    def get_input_data_rate(job_name: str, base_url: str = "localhost"):
        '''
        :param base_url:
        :param job_name:
        :return: input data rate of a Job (count per second)
        '''
        response = requests.get(f'http://{base_url}:9090/api/v1/query', params={'query': 'flink_taskmanager_job_task_operator_numRecordsInPerSecond'})
        # response.json()['data']['result'][0] to [N] is the source, sink operators of each job, weird!
        result = response.json()['data']['result']
        for op_count in range(len(result)):
            if "Sink" in result[op_count]['metric']['operator_name']:
                if result[op_count]['metric']['job_name'] == job_name:
                    return result[op_count]['value'][1]

    @staticmethod
    def get_output_data_rate(job_name: str, base_url: str = "localhost"):
        '''
        :param base_url:
        :param job_name:
        :return: output data rate of a Job (count per second)
        '''
        response = requests.get(f'http://{base_url}:9090/api/v1/query', params={'query': 'flink_taskmanager_job_task_operator_numRecordsOutPerSecond'})
        # response.json()['data']['result'][0] to [N] is the source, sink operators of each job, weird!
        result = response.json()['data']['result']
        for op_count in range(len(result)):
            if "Source" in result[op_count]['metric']['operator_name']:
                if result[op_count]['metric']['job_name'] == job_name:
                    return result[op_count]['value'][1]

    @staticmethod
    def get_input_records_count(job_name: str, base_url: str = "localhost"):
        '''
        :param base_url:
        :param job_name:
        :return: total number of records in for a Job
        '''
        response = requests.get(f'http://{base_url}:9090/api/v1/query', params={'query': 'flink_taskmanager_job_task_operator_numRecordsIn'})
        # response.json()['data']['result'][0] to [N] is the source, sink operators of each job, weird!
        result = response.json()['data']['result']
        for op_count in range(len(result)):
            if "Sink" in result[op_count]['metric']['operator_name']:
                if result[op_count]['metric']['job_name'] == job_name:
                    return result[op_count]['value'][1]

    @staticmethod
    def get_output_records_count(job_name: str, base_url: str = "localhost"):
        '''
        :param base_url:
        :param job_name:
        :return: total number of records out for a Job
        '''
        response = requests.get(f'http://{base_url}:9090/api/v1/query', params={'query': 'flink_taskmanager_job_task_operator_numRecordsOut'})
        # response.json()['data']['result'][0] to [N] is the source, sink operators of each job, weird!
        result = response.json()['data']['result']
        for op_count in range(len(result)):
            if "Source" in result[op_count]['metric']['operator_name']:
                if result[op_count]['metric']['job_name'] == job_name:
                    return result[op_count]['value'][1]

    @staticmethod
    def get_total_task_slots(base_url: str = "localhost"):
        '''
        :param base_url:
        :return: total number of task slot for the JobManager (assuming a node has only 1 JM)
        '''
        response = requests.get(f'http://{base_url}:9090/api/v1/query', params={'query': 'flink_jobmanager_taskSlotsTotal'})
        # response.json()['data']['result'][0] to [N] is the source, sink operators of each job, weird!
        result = response.json()['data']['result']
        return result[0]['value'][1]

    @staticmethod
    def get_available_task_slots(base_url: str = "localhost"):
        '''
        :param base_url:
        :return: number of available task slot for JobMananger (assuming a node has only 1 JM)
        '''
        response = requests.get(f'http://{base_url}:9090/api/v1/query', params={'query': 'flink_jobmanager_taskSlotsAvailable'})
        # response.json()['data']['result'][0] to [N] is the source, sink operators of each job, weird!
        result = response.json()['data']['result']
        return result[0]['value'][1]