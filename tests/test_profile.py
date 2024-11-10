from cProfile import Profile
import pstats
from time import perf_counter

from lucytok import english
from contextlib import contextmanager


@contextmanager
def profile_and_print():
    profiler = Profile()
    profiler.enable()

    try:
        yield
    finally:
        profiler.disable()

    profiler.dump_stats("profile.prof")
    pstats.Stats(profiler).sort_stats(pstats.SortKey.CUMULATIVE).print_stats(100)
    # Save to disk


def profile_lucytok():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    with open("README.md", "r") as f:
        text = f.read()
        start = perf_counter()
        with profile_and_print():
            for _ in range(1000):
                everything(text)
        print(perf_counter() - start)


def test_profile():
    profile_lucytok()
