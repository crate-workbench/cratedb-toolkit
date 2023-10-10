# Copyright (c) 2023, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.
import logging

import sqlalchemy as sa

from cratedb_toolkit.materialized.model import MaterializedViewSettings
from cratedb_toolkit.materialized.store import MaterializedViewStore
from cratedb_toolkit.model import TableAddress

logger = logging.getLogger(__name__)


class MaterializedViewManager:
    """
    The main application, implementing basic synthetic materialized views.
    """

    def __init__(self, settings: MaterializedViewSettings):
        # Runtime context settings.
        self.settings = settings

        # Retention policy store API.
        self.store = MaterializedViewStore(settings=self.settings)

    def refresh(self, name: str):
        """
        Resolve materialized view, and refresh it.
        """
        logger.info(f"Refreshing materialized view: {name}")

        table_schema, table_name = name.split(".")
        table_address = TableAddress(schema=table_schema, table=table_name)
        mview = self.store.get_by_table(table_address)
        logger.info(f"Loaded materialized view definition: {mview}")

        sql_ddl = f"DROP TABLE IF EXISTS {mview.staging_table_fullname}"
        logger.info(f"Dropping materialized view (staging): {sql_ddl}")
        self.store.execute(sa.text(sql_ddl))

        # TODO: IF NOT EXISTS
        sql_ddl = f"CREATE TABLE {mview.staging_table_fullname} AS (\n{mview.sql}\n)"
        logger.info(f"Creating materialized view (staging): {sql_ddl}")
        self.store.execute(sa.text(sql_ddl))
        sql_refresh = f"REFRESH TABLE {mview.staging_table_fullname}"
        self.store.execute(sa.text(sql_refresh))

        # sql_ddl = f"DROP TABLE IF EXISTS {mview.table_fullname}"
        # logger.info(f"Dropping materialized view (live): {sql_ddl}")
        # self.store.execute(sa.text(sql_ddl))

        # FIXME: SQLParseException[Target table name must not include a schema]
        sql_ddl = f"ALTER TABLE {mview.staging_table_fullname} RENAME TO {mview.table_name}"
        logger.info(f"Activating materialized view: {sql_ddl}")
        self.store.execute(sa.text(sql_ddl))
        sql_refresh = f"REFRESH TABLE {mview.table_fullname}"
        self.store.execute(sa.text(sql_refresh))
