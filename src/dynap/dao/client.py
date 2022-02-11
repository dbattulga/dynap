from __future__ import absolute_import, annotations

import urllib.parse  # if password contains '@' we might want to escape
from abc import ABC, abstractmethod
from typing import List

from pymongo import MongoClient

from dynap.dao.common import DaoEntryNotFound
from dynap.model.client import Client, logger


class ClientDao(ABC):
    """
    Data Access Object Interface for Events.
    This interface defines the standard operations that can be applied to events.
    """

    @abstractmethod
    def save(self, client: Client) -> None:
        pass

    @abstractmethod
    def get(self, client_id: str) -> Client:
        pass

    @abstractmethod
    def list(self) -> List[Client]:
        pass

    @abstractmethod
    def update(self, client: Client) -> None:
        pass

    @abstractmethod
    def delete(self, client_id: str) -> None:
        pass


class MockClientDao(ClientDao):

    def save(self, client: Client) -> None:
        raise NotImplemented("This method should be mocked")

    def get(self, client_id: str) -> Client:
        raise NotImplemented("This method should be mocked")

    def list(self) -> List[Client]:
        raise NotImplemented("This method should be mocked")

    def update(self, client: Client) -> None:
        raise NotImplemented("This method should be mocked")

    def delete(self, client_id: str) -> None:
        raise NotImplemented("This method should be mocked")


class MongoDbClientDao(ClientDao):

    def __init__(self, client: MongoClient, database_name) -> None:
        self._client = client
        self.database = self._client[database_name]
        self.collection = self.database["clients"]

    def save(self, client: Client) -> None:
        logger.debug(f"Saving client {client.client_id}.")
        self.collection.insert_one(client.to_repr())

    def get(self, client_id: str) -> Client:
        logger.debug(f"Getting client {client_id}.")
        result = self.collection.find_one({"client_id": client_id})
        if result is None:
            raise DaoEntryNotFound
        else:
            result.pop('_id', None)
            return Client.from_repr(result)

    def list(self) -> List[Client]:
        results = []
        result = self.collection.find({})
        for r in result:
            r.pop('_id', None)
            results.append(Client.from_repr(r))
        return results

    def update(self, client: Client) -> None:
        logger.debug(f"Updating client {client.client_id}.")
        result = self.collection.replace_one({"client_id": client.client_id}, client.to_repr())

    def delete(self, client_id: str) -> None:
        logger.debug(f"Deleting client {client_id}.")
        result = self.collection.delete_one({"client_id": client_id})

    @staticmethod
    def build(host: str, port: int, username: str, password, database: str) -> MongoDbClientDao:
        client = MongoClient(f"mongodb://{username}:{urllib.parse.quote_plus(password)}@{host}:{port}")
        return MongoDbClientDao(client, database)
