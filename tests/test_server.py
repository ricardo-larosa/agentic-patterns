from agentic_tot.server import get_the_secret_fact


def test_get_the_secret_fact():
    assert get_the_secret_fact("foo") == "foo"
