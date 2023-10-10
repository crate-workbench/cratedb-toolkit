import pytest

from cratedb_toolkit.materialized.model import MaterializedViewSettings
from cratedb_toolkit.materialized.schema import setup_schema
from cratedb_toolkit.materialized.store import MaterializedViewStore
from cratedb_toolkit.model import DatabaseAddress
from cratedb_toolkit.util.database import DatabaseAdapter


@pytest.fixture()
def settings(cratedb):
    """
    Provide configuration and runtime settings object, parameterized for the test suite.
    """
    database_url = cratedb.get_connection_url()
    settings = MaterializedViewSettings(database=DatabaseAddress.from_string(database_url))
    # job_settings.policy_table.schema = TESTDRIVE_EXT_SCHEMA
    return settings


@pytest.fixture()
def database(cratedb, settings):
    """
    Provide a client database adapter, which is connected to the test database instance.
    """
    yield DatabaseAdapter(dburi=settings.database.dburi)


@pytest.fixture()
def store(database, settings):
    """
    Provide a client database adapter, which is connected to the test database instance.
    The retention policy database table schema has been established.
    """
    # dcdcd
    setup_schema(settings=settings)
    store = MaterializedViewStore(settings=settings)
    yield store
