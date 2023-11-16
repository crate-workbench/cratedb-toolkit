# Copyright (c) 2023, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.
import responses

import cratedb_toolkit


@responses.activate
def test_example_cloud_cluster_exists(mocker, mock_cloud_cluster_exists):
    """
    Verify that the program `examples/cloud_cluster.py` works.
    In this case, there is a mock which pretends the cluster already exists.
    """

    cratedb_toolkit.configure(
        settings_accept_env=True,
    )

    mocker.patch.dict(
        "os.environ",
        {
            "CRATEDB_CLOUD_SUBSCRIPTION_ID": "f33a2f55-17d1-4f21-8130-b6595d7c52db",
            "CRATEDB_CLOUD_CLUSTER_NAME": "testcluster",
            "CRATEDB_USERNAME": "crate",
        },
    )
    from examples.cloud_cluster import main

    main()


@responses.activate
def test_example_cloud_cluster_with_deploy(mocker, mock_cloud_cluster_deploy):
    """
    Verify that the program `examples/cloud_cluster.py` works.
    In this case, mocking-wise, there is no cluster, but the test exercises a full cluster deployment.
    """

    cratedb_toolkit.configure(
        settings_accept_env=True,
    )

    mocker.patch.dict(
        "os.environ",
        {
            "CRATEDB_CLOUD_SUBSCRIPTION_ID": "f33a2f55-17d1-4f21-8130-b6595d7c52db",
            "CRATEDB_CLOUD_CLUSTER_NAME": "testcluster",
            "CRATEDB_USERNAME": "crate",
        },
    )
    from examples.cloud_cluster import main

    main()


@responses.activate
def test_example_cloud_import(mocker, mock_cloud_import):
    """
    Verify that the program `examples/cloud_import.py` works.
    """

    cratedb_toolkit.configure(
        settings_accept_env=True,
    )

    mocker.patch.dict(
        "os.environ",
        {
            "CRATEDB_CLOUD_CLUSTER_ID": "e1e38d92-a650-48f1-8a70-8133f2d5c400",
        },
    )
    from examples.cloud_import import main

    main()