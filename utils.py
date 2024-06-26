import time


UNSET = object()


def get_path(obj, path, default=UNSET):
    """
    Retrieve a subobject in a nested structure like a dict or list.

    If the subobject is not found, raise an exception unless `default` is
    provided, in which case `default` will be returned.
    """
    if path == []:
        return obj
    else:
        try:
            return get_path(obj[path[0]], path[1:], default)
        except (LookupError, TypeError):
            if default is UNSET:
                raise
            else:
                return default


def query_eventually(
    query,
    predicate=lambda x: x,
    interval=1,
    max_time=3,
    info_log=print,
):
    """
    Wait `max_time` seconds for `predicate(query())` to become true.

    `predicate` is optional.  By default, the `predicate` checks that the
    result from the `query` is truthy.

    Polls for the predicate every `interval` seconds.

    This is like `query()`, except instead of just polling the predicate, this
    actually takes responsibility for making the query that the predicate
    checks.  This allows it to report the state of the query when it fails,
    giving better transparency into the state of the system at failure.

    A useful trick is to just roll a bunch of good diagnostics into the query,
    and then make the predicate check only the important parts.  That way, if
    the poll times out, you get a nice big blob of diagnostic information at
    the time it failed.
    """

    end_time = time.time() + max_time

    while time.time() < end_time:
        query_result = query()
        if predicate(query_result):
            return query_result
        info_log(
            f"Predicate {predicate.__name__} current value: {query_result}. "
            f"Polling interval: {interval} seconds. {end_time - time.time()} "
            f"seconds remaining until timeout."
        )
        time.sleep(interval)

    # The else branch is reached if the while exits without the break
    else:
        raise RuntimeError(
            f"Timeout: predicate {predicate.__name__} not truthy after "
            f"{max_time} seconds.  Last query value from {query.__name__} "
            f"(next line):\n{query_result}"
        )


