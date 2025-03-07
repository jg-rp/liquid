from liquid import CachingDictLoader
from liquid import Environment


def test_caching_choice_loader() -> None:
    loader = CachingDictLoader(
        {
            "a": "Hello, {{ you }}!",
            "b": "the quick brown {{ animal | default: 'fox' }}",
        }
    )

    env = Environment(loader=loader)
    assert len(loader.cache) == 0
    template = env.get_template("a")
    assert template.render(you="World") == "Hello, World!"
    assert len(loader.cache) == 1
    template = env.get_template("b")
    assert template.render() == "the quick brown fox"
    assert len(loader.cache) == 2

    assert env.get_template("b") is template
