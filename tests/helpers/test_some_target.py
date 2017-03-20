import pytest

from paip.helpers import SomeTarget


def test_exists():
    some_target = SomeTarget(
        destination_dir=pytest.helpers.file('Cohort1/coverage_plots'),
        suffix='.png',
    )

    assert some_target.exists()

    some_target = SomeTarget(
        destination_dir=pytest.helpers.file('Cohort1/coverage_plots'),
        suffix='non_existent',
    )

    assert not some_target.exists()

