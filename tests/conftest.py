# Copyright (c) 2021-2023, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.
import json
import os

import pytest
import responses

from cratedb_toolkit.api.main import ManagedClusterSettings
from cratedb_toolkit.testing.testcontainers.util import PytestTestcontainerAdapter
from cratedb_toolkit.util import DatabaseAdapter
from cratedb_toolkit.util.common import setup_logging

# Use different schemas for storing the subsystem database tables, and the
# test/example data, so that they do not accidentally touch the default `doc`
# schema.
TESTDRIVE_EXT_SCHEMA = "testdrive-ext"
TESTDRIVE_DATA_SCHEMA = "testdrive-data"

RESET_TABLES = [
    f'"{TESTDRIVE_EXT_SCHEMA}"."retention_policy"',
    f'"{TESTDRIVE_DATA_SCHEMA}"."raw_metrics"',
    f'"{TESTDRIVE_DATA_SCHEMA}"."sensor_readings"',
    f'"{TESTDRIVE_DATA_SCHEMA}"."testdrive"',
    f'"{TESTDRIVE_DATA_SCHEMA}"."foobar"',
    f'"{TESTDRIVE_DATA_SCHEMA}"."foobar_unique_single"',
    f'"{TESTDRIVE_DATA_SCHEMA}"."foobar_unique_composite"',
    # cratedb_toolkit.io.{influxdb,mongodb}
    '"testdrive"."demo"',
]


class CrateDBFixture(PytestTestcontainerAdapter):
    """
    A little helper wrapping Testcontainer's `CrateDBContainer` and
    CrateDB Toolkit's `DatabaseAdapter`, agnostic of the test framework.
    """

    def __init__(self):
        self.container = None
        self.database: DatabaseAdapter = None
        super().__init__()

    def setup(self):
        from cratedb_toolkit.testing.testcontainers.cratedb import CrateDBContainer

        # TODO: Make image name configurable.
        self.container = CrateDBContainer("crate/crate:nightly")
        self.container.start()
        self.database = DatabaseAdapter(dburi=self.get_connection_url())

    def reset(self):
        # TODO: Make list of tables configurable.
        for reset_table in RESET_TABLES:
            self.database.connection.exec_driver_sql(f"DROP TABLE IF EXISTS {reset_table};")

    def get_connection_url(self, *args, **kwargs):
        return self.container.get_connection_url(*args, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def configure_database_schema(session_mocker):
    """
    Configure the machinery to use a different schema for storing subsystem database
    tables, so that they do not accidentally touch the production system.

    If not configured otherwise, the test suite currently uses `testdrive-ext`.
    """
    session_mocker.patch.dict("os.environ", {"CRATEDB_EXT_SCHEMA": TESTDRIVE_EXT_SCHEMA})


@pytest.fixture(scope="session")
def cratedb_service():
    """
    Provide a CrateDB service instance to the test suite.
    """
    db = CrateDBFixture()
    db.reset()
    yield db
    db.stop()


@pytest.fixture(scope="function")
def cratedb(cratedb_service):
    """
    Provide a fresh canvas to each test case invocation, by resetting database content.
    """
    cratedb_service.reset()
    yield cratedb_service


@pytest.fixture
def mock_cloud_cluster_exists(cratedb):
    """
    Mock a CrateDB Cloud API conversation, pretending a cluster exists.
    """
    responses.add_passthru("http+docker://localhost/")
    responses.add(
        method="GET",
        url="https://console.cratedb.cloud/api/v2/clusters/",
        json=[
            {
                "id": "e1e38d92-a650-48f1-8a70-8133f2d5c400",
                "url": cratedb.get_connection_url(),
                "project_id": "3b6b7c82-d0ab-458c-ae6f-88f8346765ee",
                "name": "testcluster",
            }
        ],
    )


@pytest.fixture
def mock_cloud_cluster_deploy(cratedb):
    """
    Mock a CrateDB Cloud API conversation, for exercising a full deployment process.
    """
    responses.add_passthru("http+docker://localhost/")

    callcount = 0

    def cluster_list_callback(request):
        nonlocal callcount
        callcount += 1
        headers = {}
        if callcount == 1:
            data = []
        else:
            data = [
                {
                    "id": "e1e38d92-a650-48f1-8a70-8133f2d5c400",
                    "url": cratedb.get_connection_url(),
                    "project_id": "3b6b7c82-d0ab-458c-ae6f-88f8346765ee",
                    "name": "testcluster",
                }
            ]
        return 200, headers, json.dumps(data)

    responses.add_callback(
        method="GET",
        url="https://console.cratedb.cloud/api/v2/clusters/",
        callback=cluster_list_callback,
    )

    responses.add(
        method="GET",
        url="https://console.cratedb.cloud/api/v2/projects/",
        json=[],
    )

    responses.add(
        method="POST",
        url="https://console.cratedb.cloud/api/v2/projects/",
        json={"id": "3b6b7c82-d0ab-458c-ae6f-88f8346765ee"},
    )

    responses.add(
        method="GET",
        url="https://console.cratedb.cloud/api/v2/projects/3b6b7c82-d0ab-458c-ae6f-88f8346765ee/",
        json={},
    )


@pytest.fixture
def mock_cloud_import():
    """
    Mock a CrateDB Cloud API conversation, pretending to run a successful data import.
    """
    responses.add(
        method="GET",
        url="https://console.cratedb.cloud/api/v2/clusters/e1e38d92-a650-48f1-8a70-8133f2d5c400/",
        json={
            "id": "e1e38d92-a650-48f1-8a70-8133f2d5c400",
            "project_id": "3b6b7c82-d0ab-458c-ae6f-88f8346765ee",
            "url": "https://testdrive.example.org:4200/",
            "name": "testcluster",
        },
    )
    responses.add(
        method="POST",
        url="https://console.cratedb.cloud/api/v2/clusters/e1e38d92-a650-48f1-8a70-8133f2d5c400/import-jobs/",
        json={"id": "testdrive-job-id", "status": "REGISTERED"},
    )
    responses.add(
        method="GET",
        url="https://console.cratedb.cloud/api/v2/clusters/e1e38d92-a650-48f1-8a70-8133f2d5c400/import-jobs/",
        json=[
            {
                "id": "testdrive-job-id",
                "status": "SUCCEEDED",
                "progress": {"message": "Import succeeded"},
                "destination": {"table": "basic"},
            }
        ],
    )


@pytest.fixture(scope="session", autouse=True)
def reset_environment():
    """
    Reset all environment variables in use, so that they do not pollute the test suite.
    """
    envvars = []
    specs = ManagedClusterSettings.settings_spec
    for spec in specs:
        envvars.append(spec.click.envvar)
    for envvar in envvars:
        try:
            del os.environ[envvar]
        except KeyError:
            pass


setup_logging()
