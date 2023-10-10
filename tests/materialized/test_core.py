import re

import pytest
from sqlalchemy.exc import ProgrammingError

from cratedb_toolkit.materialized.core import MaterializedViewManager
from cratedb_toolkit.materialized.model import MaterializedView
from tests.retention.conftest import TESTDRIVE_DATA_SCHEMA, TESTDRIVE_EXT_SCHEMA


@pytest.fixture
def mview(store) -> MaterializedView:
    item = MaterializedView(
        table_schema=TESTDRIVE_DATA_SCHEMA,
        table_name="foobar",
        sql=f'SELECT * FROM "{TESTDRIVE_DATA_SCHEMA}"."raw_metrics"',
        id=None,
    )
    store.create(item, ignore="DuplicateKeyException")
    return item


def foo(database):
    sdcsdc
    # database.run_sql("DROP TABLE IF EXISTS testdrive.foobar;")
    database.run_sql(f'CREATE TABLE "{TESTDRIVE_EXT_SCHEMA}"."foobar" AS SELECT 1;')
    database.run_sql(f'CREATE TABLE "{TESTDRIVE_DATA_SCHEMA}"."raw_metrics" AS SELECT 1;')
    # database.run_sql('CREATE TABLE "testdrive"."foobar" AS SELECT 1;')


def test_materialized_undefined(settings, database, store):
    mvm = MaterializedViewManager(settings=settings)
    with pytest.raises(KeyError) as ex:
        mvm.refresh("unknown.unknown")
    ex.match("Synthetic materialized table definition does not exist: unknown.unknown")


def test_materialized_missing_schema(settings, database, store, mview):
    mvm = MaterializedViewManager(settings=settings)
    with pytest.raises(ProgrammingError) as ex:
        mvm.refresh(f"{TESTDRIVE_DATA_SCHEMA}.foobar")
    ex.match(re.escape("SchemaUnknownException[Schema 'testdrive-data' unknown"))


def test_materialized_missing_table(settings, database, store, mview):
    database.run_sql(f'CREATE TABLE "{TESTDRIVE_DATA_SCHEMA}"."foobar" AS SELECT 1;')

    mvm = MaterializedViewManager(settings=settings)
    with pytest.raises(ProgrammingError) as ex:
        mvm.refresh(f"{TESTDRIVE_DATA_SCHEMA}.foobar")
    ex.match(re.escape("RelationUnknown[Relation 'testdrive-data.raw_metrics' unknown]"))


def te2st_materialized_success(settings, database, store, mview):
    # TODO: Does not work.
    # database.run_sql("CREATE TABLE IF NOT EXISTS testdrive.foobar AS SELECT 1")

    # database.run_sql("DROP TABLE IF EXISTS testdrive.foobar;")
    # database.run_sql('CREATE TABLE "testdrive"."raw_data" AS SELECT 1;')
    # database.run_sql('CREATE TABLE "testdrive"."foobar" AS SELECT 1;')
    # database.run_sql('REFRESH TABLE "testdrive"."foobar";')

    mvm = MaterializedViewManager(settings=settings)
    print(mvm.refresh("testdrive.foobar"))
