import logging

import click
from click_aliases import ClickAliasedGroup

from cratedb_toolkit.api.main import ClusterBase, ManagedCluster, StandaloneCluster
from cratedb_toolkit.common import option_cluster_id, option_cluster_name
from cratedb_toolkit.model import DatabaseAddress, InputOutputResource, TableAddress
from cratedb_toolkit.util.cli import boot_click, make_command

logger = logging.getLogger(__name__)


@click.group(cls=ClickAliasedGroup)  # type: ignore[arg-type]
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    """
    Load data into CrateDB.
    """
    return boot_click(ctx, verbose, debug)


@make_command(cli, name="table")
@click.argument("url")
@option_cluster_id
@option_cluster_name
@click.option(
    "--cratedb-sqlalchemy-url", envvar="CRATEDB_SQLALCHEMY_URL", type=str, required=False, help="CrateDB SQLAlchemy URL"
)
@click.option("--cratedb-http-url", envvar="CRATEDB_HTTP_URL", type=str, required=False, help="CrateDB HTTP URL")
@click.option("--schema", envvar="CRATEDB_SCHEMA", type=str, required=False, help="Schema where to import the data")
@click.option("--table", envvar="CRATEDB_TABLE", type=str, required=False, help="Table where to import the data")
@click.option("--format", "format_", type=str, required=False, help="File format of the import resource")
@click.option("--compression", type=str, required=False, help="Compression format of the import resource")
@click.pass_context
def load_table(
    ctx: click.Context,
    url: str,
    cluster_id: str,
    cluster_name: str,
    cratedb_sqlalchemy_url: str,
    cratedb_http_url: str,
    schema: str,
    table: str,
    format_: str,
    compression: str,
):
    """
    Import data into CrateDB and CrateDB Cloud clusters.
    """

    error_message = (
        "Either CrateDB Cloud Cluster identifier or CrateDB SQLAlchemy or HTTP URL needs to be supplied. "
        "Use --cluster-id / --cluster-name / --cratedb-sqlalchemy-url / --cratedb-http-url CLI options "
        "or CRATEDB_CLOUD_CLUSTER_ID / CRATEDB_CLOUD_CLUSTER_NAME / CRATEDB_SQLALCHEMY_URL / CRATEDB_HTTP_URL "
        "environment variables."
    )

    # Encapsulate source and target parameters.
    source = InputOutputResource(url=url, format=format_, compression=compression)
    target = TableAddress(schema=schema, table=table)

    # Dispatch "load table" operation.
    # TODO: Unify cluster factory.
    cluster: ClusterBase
    if cluster_id is not None or cluster_name is not None:
        cluster = ManagedCluster(id=cluster_id, name=cluster_name)
    elif cratedb_sqlalchemy_url or cratedb_http_url:
        if cratedb_sqlalchemy_url:
            address = DatabaseAddress.from_string(cratedb_sqlalchemy_url)
        elif cratedb_http_url:
            address = DatabaseAddress.from_httpuri(cratedb_sqlalchemy_url)
        cluster = StandaloneCluster(address=address)
    else:
        raise KeyError(error_message)
    return cluster.load_table(source=source, target=target)
