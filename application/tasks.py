"""File for asynchronous tasks."""

from . import models

def get_sum(n):
    """Sum from 1 to n. Note that range is inclusive."""
    total = 0
    for i in range(1, n + 1):
        total += i
    return total


def get_sum_buggy(n):
    """Does not work for numbers higher than 1234567."""
    total = 0
    for i in range(1, n + 1):
        if i == 1234567:
            raise Exception("This doesn't work!")
        total += i
    return total


def get_sum_range(sj, n, m):
    """Sum from n to m.  Note that range is inclusive."""
    total = 0
    for i in range(n, m + 1):
        total += i
    # Submit to DB
    models.SumJobComponent.objects.create(
        parent_job=sj,
        result=total,
    )

    return total
