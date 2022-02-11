from __future__ import absolute_import, annotations

from dynap.dao.job import JobDao, MockJobDao, MongoDbJobDao
from dynap.dao.client import ClientDao, MockClientDao, MongoDbClientDao


class DaoCollector:

    def __init__(self, job_dao: JobDao, client_dao: ClientDao) -> None:
        super().__init__()
        self.job_dao = job_dao
        self.client_dao = client_dao


class DaoCollectorBuilder:

    @staticmethod
    def mongo_db(host: str, port: int, username: str, password, mongo_db_database: str) -> DaoCollector:
        job_dao = MongoDbJobDao.build(
                host=host,
                port=port,
                username=username,
                password=password,
                database=mongo_db_database
            )
        client_dao = MongoDbClientDao.build(
            host=host,
            port=port,
            username=username,
            password=password,
            database=mongo_db_database
        )
        return DaoCollector(job_dao=job_dao, client_dao=client_dao)

    @staticmethod
    def mock() -> DaoCollector:
        return DaoCollector(
            MockJobDao(), MockClientDao()
        )

