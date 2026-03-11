from datetime import date

import pytest

from app.schemas.circle import Frequency, compute_end_date


@pytest.mark.parametrize(
    "start, payout_count, frequency, expected",
    [
        # From spec acceptance scenarios
        (date(2026, 4, 1), 4, Frequency.monthly,   date(2026, 8, 1)),
        (date(2026, 4, 1), 4, Frequency.weekly,    date(2026, 4, 29)),
        (date(2026, 4, 1), 2, Frequency.quarterly, date(2026, 10, 1)),
        # Additional coverage
        (date(2026, 4, 1), 7, Frequency.daily,     date(2026, 4, 8)),
        (date(2026, 4, 1), 3, Frequency.bi_weekly, date(2026, 5, 13)),
        # Month-end edge case: Jan 31 + 1 month = Feb 28
        (date(2026, 1, 31), 1, Frequency.monthly,  date(2026, 2, 28)),
    ],
)
def test_compute_end_date(start, payout_count, frequency, expected):
    assert compute_end_date(start, payout_count, frequency) == expected
