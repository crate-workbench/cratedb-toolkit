# Copyright (c) 2023, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.


def test_example_materialized_view(store):
    """
    Verify that the program `examples/materialized_view.py` works.
    """
    from examples.materialized_view import main

    main(dburi=store.database.dburi)
