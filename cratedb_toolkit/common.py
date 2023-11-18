import click

option_cluster_id = click.option(
    "--cluster-id", envvar="CRATEDB_CLOUD_CLUSTER_ID", type=str, required=False, help="CrateDB Cloud cluster identifier"
)
option_cluster_name = click.option(
    "--cluster-name", envvar="CRATEDB_CLOUD_CLUSTER_NAME", type=str, required=False, help="CrateDB Cloud cluster name"
)
