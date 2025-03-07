from liquid import render


def test_cycle_without_name() -> None:
    source = ",".join(
        [
            "{% cycle 1, 2, 3 %}",
            "{% cycle 'x', 'y', 'z' %}",
            "{% cycle 1, 2, 3 %}",
        ]
    )

    assert render(source) == "1,x,2"


def test_cycle_wraps() -> None:
    source = ",".join(
        [
            "{% cycle 'some', 'other' %}",
            "{% cycle 'some', 'other' %}",
            "{% cycle 'some', 'other' %}",
        ]
    )

    assert render(source) == "some,other,some"


def test_named_cycle_groups() -> None:
    """Test that named cycles ignore arguments."""
    source = ",".join(
        [
            "{% cycle 'a':  1, 2, 3 %}",
            "{% cycle 'a': 'x', 'y', 'z' %}",
            "{% cycle 'a': 1, 2, 3 %}",
        ]
    )

    assert render(source) == "1,y,3"


def test_named_cycles_with_shrinking_lengths() -> None:
    """Test that we handle cycles with a shrinking number of arguments."""
    source = ",".join(
        [
            "{% cycle 'a':  1, 2, 3 %}",
            "{% cycle 'a': 'x', 'y' %}",
            "{% cycle 'a': 'x' %}",
        ]
    )

    assert render(source) == "1,y,x"


def test_named_cycles_with_growing_lengths() -> None:
    """Test that we handle cycles with a growing number of arguments."""
    source = ",".join(
        [
            "{% cycle 'a':  1, 2 %}",
            "{% cycle 'a': 'x', 'y', 'z' %}",
            "{% cycle 'a': 'x', 'y', 'z' %}",
        ]
    )

    assert render(source) == "1,y,z"


def test_named_cycles_with_changing_lengths() -> None:
    source = "".join(
        [
            "{% cycle 'a':  '1', '2' %}",
            "{% cycle 'a':  '1', '2', '3' %}",
            "{% cycle 'a':  '1', %}",
        ]
    )

    assert render(source) == "12"
