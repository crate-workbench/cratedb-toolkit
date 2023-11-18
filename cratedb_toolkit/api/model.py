import abc
import dataclasses

import crate.client
import sqlalchemy as sa

from cratedb_toolkit.model import InputOutputResource, TableAddress
from cratedb_toolkit.util import DatabaseAdapter


@dataclasses.dataclass
class ClientBundle:
    """
    Provide userspace with a client bundle of connections to the database.
    """

    adapter: DatabaseAdapter
    dbapi: crate.client.connection.Connection
    sqlalchemy: sa.Engine


class ClusterBase(abc.ABC):
    @abc.abstractmethod
    def load_table(self, source: InputOutputResource, target: TableAddress):
        raise NotImplementedError("Child class needs to implement this method")

    @abc.abstractmethod
    def get_client_bundle(self) -> ClientBundle:
        raise NotImplementedError("Child class needs to implement this method")
