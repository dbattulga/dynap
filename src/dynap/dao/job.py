from __future__ import absolute_import, annotations

import urllib.parse  # if password contains '@' we might want to escape
from abc import ABC, abstractmethod
from typing import List

from pymongo import MongoClient

from dynap.dao.common import DaoEntryNotFound
from dynap.model.job import DeployedJob, logger


class JobDao(ABC):
    """
    Data Access Object Interface for Events.
    This interface defines the standard operations that can be applied to events.
    """

    @abstractmethod
    def save(self, job: DeployedJob) -> None:
        pass

    @abstractmethod
    def get(self, job_id: str) -> DeployedJob:
        pass

    @abstractmethod
    def list(self) -> List[DeployedJob]:
        pass

    @abstractmethod
    def update(self, job: DeployedJob) -> None:
        pass

    @abstractmethod
    def delete(self, job_id: str) -> None:
        pass


class MockJobDao(JobDao):

    def save(self, job: DeployedJob) -> None:
        raise NotImplemented("This method should be mocked")

    def get(self, job_id: str) -> DeployedJob:
        raise NotImplemented("This method should be mocked")

    def list(self) -> List[DeployedJob]:
        raise NotImplemented("This method should be mocked")

    def update(self, job: DeployedJob) -> None:
        raise NotImplemented("This method should be mocked")

    def delete(self, job_id: str) -> None:
        raise NotImplemented("This method should be mocked")


class MongoDbJobDao(JobDao):

    def __init__(self, client: MongoClient, database_name) -> None:
        self._client = client
        self.database = self._client[database_name]
        self.collection = self.database["jobs"]

    def save(self, job: DeployedJob) -> None:
        logger.debug(f"Saving job {job.job_id}.")
        self.collection.insert_one(job.to_repr())

    def get(self, job_id: str) -> DeployedJob:
        logger.debug(f"Getting job {job_id}.")
        result = self.collection.find_one({"job_id": job_id})
        if result is None:
            raise DaoEntryNotFound
        else:
            result.pop('_id', None)
            return DeployedJob.from_repr(result)

    def list(self) -> List[DeployedJob]:
        results = []
        result = self.collection.find({})
        for r in result:
            r.pop('_id', None)
            results.append(DeployedJob.from_repr(r))
        return results

    def update(self, job: DeployedJob) -> None:
        logger.debug(f"Updating job {job.job_id}.")
        result = self.collection.replace_one({"job_id": job.job_id}, job.to_repr())

    def delete(self, job_id: str) -> None:
        logger.debug(f"Deleting job {job_id}.")
        result = self.collection.delete_one({"job_id": job_id})

    @staticmethod
    def build(host: str, port: int, username: str, password, database: str) -> MongoDbJobDao:
        client = MongoClient(f"mongodb://{username}:{urllib.parse.quote_plus(password)}@{host}:{port}")
        return MongoDbJobDao(client, database)
