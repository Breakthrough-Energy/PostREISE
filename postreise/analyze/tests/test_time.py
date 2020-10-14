import pandas as pd
import pytest
import pytz

from postreise.analyze.time import (
    change_time_zone,
    is_dst,
    resample_time_series,
    slice_time_series,
)

nb_hours = 366 * 24
ts_as_data_frame = pd.DataFrame(
    {"A": [1] * nb_hours, "B": [2] * nb_hours},
    index=pd.date_range("2016-01-01", periods=nb_hours, freq="H"),
)
ts_as_series = pd.Series(
    [1] * nb_hours,
    index=pd.date_range("2016-01-01", periods=nb_hours, freq="H"),
)


def test_slicing():
    start = pd.Timestamp(2016, 3, 1)
    end = pd.Timestamp(2016, 3, 31)
    arg = (ts_as_data_frame, ts_as_series)
    for a in arg:
        ts_sliced = slice_time_series(a, start, end)
        assert ts_sliced.index[0] == start
        assert ts_sliced.index[-1] == end


def test_resampling_argument_value():
    arg = (
        (ts_as_data_frame, "Q", "mean"),
        (ts_as_series, "D", "median"),
        (ts_as_data_frame.tz_localize("UTC").tz_convert("US/Pacific"), "W", "sum"),
    )
    for a in arg:
        with pytest.raises(ValueError):
            resample_time_series(a[0], a[1], agg=a[2])


def test_daily_resampling_sum():
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D")
        assert len(a) != len(ts_resampled)
        # 366 days are available in 2016
        assert len(ts_resampled) == 366
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 1, 1))
        assert str(ts_resampled.index[-1]) == str(pd.Timestamp(2016, 12, 31))
        if i == 0:
            assert a.sum().equals(ts_resampled.sum())
        else:
            assert a.sum() == ts_resampled.sum()


def test_daily_resampling_time_shift_sum():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first day (2015/12/31) and last day (2016/12/31) are incomplete.
            # 365 full days are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 365
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-30", tz="ETC/GMT+8")
            )
        else:
            # first day (2016/01/01) and last day (2017/01/01) are incomplete.
            # 365 full days are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 365
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-02", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-31", tz="ETC/GMT-8")
            )


def test_daily_resampling_mean():
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D", agg="mean")
        assert len(a) != len(ts_resampled)
        # 366 days are available in 2016
        assert len(ts_resampled) == 366
        assert str(ts_resampled.index[1]) == str(pd.Timestamp(2016, 1, 2))
        if i == 0:
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_daily_resampling_time_shift_mean():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D", agg="mean")
        assert len(a) != len(ts_resampled)
        assert len(ts_resampled) == 366
        if i == 0:
            # first day (2015/12/31) and last day (2016/12/31) are incomplete.
            # 366 days are available in 2016 after resampling using mean.
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-31", tz="ETC/GMT+8")
            )
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            # first day (2016/01/01) and last day (2017/01/01) are incomplete.
            # 366 days are available in 2016 after resampling using mean.
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-31", tz="ETC/GMT-8")
            )
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_daily_resampling_incomplete_sum():
    start = pd.Timestamp(2016, 1, 1, 12)
    end = pd.Timestamp(2016, 1, 31, 12)
    arg = (ts_as_data_frame[start:end], ts_as_series[start:end])
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a[start:end], "D")
        assert len(a) != len(ts_resampled)
        # first day (2016/01/01) and last day (2016/01/31) are incomplete.
        # 29 days are available in Jamuary 2016 after resampling using sum.
        assert len(ts_resampled) == 29
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 1, 2))
        if i == 0:
            assert ts_resampled.sum().equals(
                pd.Series([float(29 * 24), float(29 * 2 * 24)], index=["A", "B"])
            )
        else:
            assert ts_resampled.sum() == 29 * 24


def test_daily_resampling_incomplete_and_time_shift_sum():
    start = pd.Timestamp(2016, 1, 1, 18)
    end = pd.Timestamp(2016, 1, 31, 18)
    arg = (
        ts_as_data_frame[start:end].tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series[start:end].tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first day (2016/01/01) and last day (2016/01/31) are incomplete.
            # 29 full days are available in Jamuary 2016 after resampling using sum.
            assert len(ts_resampled) == 29
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-02", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-30", tz="ETC/GMT+8")
            )
        else:
            # first day (2016/01/02) and last day (2016/02/01) are incomplete.
            # 29 full days are available in January 2016 after resampling using sum.
            assert len(ts_resampled) == 29
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-31", tz="ETC/GMT-8")
            )


def test_daily_resampling_incomplete_mean():
    start = pd.Timestamp(2016, 1, 1, 12)
    end = pd.Timestamp(2016, 1, 31, 12)
    arg = (ts_as_data_frame[start:end], ts_as_series[start:end])
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D", agg="mean")
        # first day (2016/01/01) and last day (2016/01/31) are incomplete.
        # 31 days are available in January 2016 after resampling using mean.
        assert len(ts_resampled) == 31
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 1, 1))
        assert str(ts_resampled.index[-1]) == str(pd.Timestamp(2016, 1, 31))
        if i == 0:
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_daily_resampling_incomplete_and_time_shift_mean():
    start = pd.Timestamp(2016, 1, 1, 18)
    end = pd.Timestamp(2016, 1, 31, 18)
    arg = (
        ts_as_data_frame[start:end].tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series[start:end].tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "D", agg="mean")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first day (2016/01/01) and last day (2016/01/31) are incomplete.
            # 31 days are available in January 2016 when resampling using mean.
            assert len(ts_resampled) == 31
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-31", tz="ETC/GMT+8")
            )
        else:
            # first day (2016/01/02) and last day (2016/02/01) are incomplete.
            # 30 days are available in January 2016 when resampling using mean.
            assert len(ts_resampled) == 30
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-02", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-31", tz="ETC/GMT-8")
            )


def test_weekly_resampling_sum():
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W")
        assert len(a) != len(ts_resampled)
        # first week (2015/12/28) is incomplete.
        # 52 full weeks are available in 2016 after resampling using sum.
        assert len(ts_resampled) == 52
        assert ts_resampled.index.dayofweek[0] == 6  # week starts on Sunday
        if i == 0:
            assert not a.sum().equals(ts_resampled.sum())
        else:
            assert a.sum() != ts_resampled.sum()


def test_weekly_resampling_time_shift_sum():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first week (2015/12/28) and last week (2016/12/25) are incomplete.
            # 51 full weeks are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 51
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-18", tz="ETC/GMT+8")
            )
        else:
            # first week (2015/12/28) is incomplete.
            # 52 full weeks are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 52
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-25", tz="ETC/GMT-8")
            )


def test_weekly_resampling_mean():
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W", agg="mean")
        assert len(a) != len(ts_resampled)
        # first week (2015/12/28) is incomplete.
        # 52 weeks are available in 2016 after resampling using sum.
        assert len(ts_resampled) == 52
        assert ts_resampled.index.dayofweek[0] == 6  # week starts on Sunday
        if i == 0:
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_weekly_resampling_time_shift_mean():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W", agg="mean")
        assert len(a) != len(ts_resampled)
        assert len(ts_resampled) == 52
        if i == 0:
            # first week (2015/12/28) and last wekk (2016/12/25) are incomplete.
            # 52 weeks are available in 2016 after resampling using mean.
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-25", tz="ETC/GMT+8")
            )

        else:
            # first week (2015/12/28) and last week (2016/12/25) are incomplete.
            # 52 weeks are available in 2016 after resampling using mean.
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-25", tz="ETC/GMT-8")
            )


def test_weekly_resampling_incomplete_sum():
    start = pd.Timestamp(2016, 1, 1, 12)
    end = pd.Timestamp(2016, 1, 31, 12)
    arg = (ts_as_data_frame[start:end], ts_as_series[start:end])
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a[start:end], "W")
        assert len(a) != len(ts_resampled)
        # first week (2015/12/28) and last week (2016/01/31) are incomplete.
        # 4 full weeks are available in 2016 after resampling using sum.
        assert len(ts_resampled) == 4
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 1, 3))
        assert str(ts_resampled.index[-1]) == str(pd.Timestamp(2016, 1, 24))
        if i == 0:
            assert ts_resampled.sum().equals(
                pd.Series([float(4 * 7 * 24), float(4 * 7 * 2 * 24)], index=["A", "B"])
            )
        else:
            assert ts_resampled.sum() == 4 * 7 * 24


def test_weekly_resampling_incomplete_and_time_shift_sum():
    start = pd.Timestamp(2016, 1, 1, 18)
    end = pd.Timestamp(2016, 1, 31, 18)
    arg = (
        ts_as_data_frame[start:end].tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series[start:end].tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first week (2015/12/28) and last week (2016/01/31) are incomplete.
            # 4 full weeks are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 4
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-24", tz="ETC/GMT+8")
            )
        else:
            # first week (2015/12/28) and last week (2016/01/31) are incomplete.
            # 4 full weeks are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 4
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-24", tz="ETC/GMT-8")
            )


def test_weekly_resampling_incomplete_mean():
    start = pd.Timestamp(2016, 1, 1, 12)
    end = pd.Timestamp(2016, 1, 31, 12)
    arg = (ts_as_data_frame[start:end], ts_as_series[start:end])
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W", agg="mean")
        # first week (2015/12/28) and last week (2016/01/31) are incomplete.
        # 5 weeks are available in 2016 after resampling using sum.
        assert len(ts_resampled) == 5
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 1, 3))
        assert str(ts_resampled.index[-1]) == str(pd.Timestamp(2016, 1, 31))
        if i == 0:
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_weekly_resampling_incomplete_and_time_shift_mean():
    start = pd.Timestamp(2016, 1, 1, 18)
    end = pd.Timestamp(2016, 1, 31, 18)
    arg = (
        ts_as_data_frame[start:end].tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series[start:end].tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "W", agg="mean")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first week (2015/12/28) and last week (2016/01/31) are incomplete.
            # 5 weeks are available in 2016 when resampling using mean.
            assert len(ts_resampled) == 5
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-31", tz="ETC/GMT+8")
            )
        else:
            # first week (2015/12/28) and last week (2016/01/31) are incomplete.
            # 5 weeks available in 2016 when resampling using mean.
            assert len(ts_resampled) == 5
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-03", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-01-31", tz="ETC/GMT-8")
            )


def test_monthly_resampling_sum():
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "M")
        assert len(a) != len(ts_resampled)
        # 12 full monts are available in 2016 when resampling using mean.
        assert len(ts_resampled) == 12
        assert str(ts_resampled.index[1]) == str(pd.Timestamp(2016, 2, 1))
        if i == 0:
            assert a.sum().equals(ts_resampled.sum())
        else:
            assert a.sum() == ts_resampled.sum()


def test_monthly_resampling_time_shift_sum():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "M")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first month (2015/12) and last month (2016/12) are incomplete.
            # 11 full months are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 11
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-11-01", tz="ETC/GMT+8")
            )
        else:
            # first month (2016/01) and last month (2017/01) are incomplete.
            # 11 full months are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 11
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-02-01", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-01", tz="ETC/GMT-8")
            )


def test_monthly_resampling_mean():
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "M", agg="mean")
        assert len(a) != len(ts_resampled)
        # 12 full months are available in 2016 when resampling using mean.
        assert len(ts_resampled) == 12
        assert str(ts_resampled.index[2]) == str(pd.Timestamp(2016, 3, 1))
        if i == 0:
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_monthly_resampling_time_shift_mean():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "M", agg="mean")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first month (2015/12) and last month (2016/12) are incomplete.
            # 12 months are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 12
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-01", tz="ETC/GMT+8")
            )
        else:
            # first month (2016/01) and last month (2017/01) are incomplete.
            # 12 months are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 12
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-12-01", tz="ETC/GMT-8")
            )


def test_monthly_resampling_incomplete_sum():
    start = pd.Timestamp(2016, 1, 15)
    end = pd.Timestamp(2016, 12, 15)
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a[start:end], "M")
        # first month (01/2016) and last month (2016/12) are incomplete.
        # 10 full months are available in 2016 when resampling using sum.
        assert len(a[start:end]) != len(ts_resampled)
        assert len(ts_resampled) == 10  # inncomplete months are clipped
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 2, 1))
        if i == 0:
            assert not a.sum().equals(ts_resampled.sum())
        else:
            assert a.sum() != ts_resampled.sum()


def test_monthly_resampling_incomplete_and_time_shift_sum():
    start = pd.Timestamp(2016, 1, 15, 18)
    end = pd.Timestamp(2016, 6, 30, 18)
    arg = (
        ts_as_data_frame[start:end].tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series[start:end].tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "M")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first month (2016/01) and last month (2016/06) are incomplete.
            # 4 full months are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 4
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-02-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-05-01", tz="ETC/GMT+8")
            )
        else:
            # first month (2016/01) and last month (2016/07) are incomplete.
            # 5 full months are available in 2016 after resampling using sum.
            assert len(ts_resampled) == 5
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-02-01", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-06-01", tz="ETC/GMT-8")
            )


def test_monthly_resampling_incomplete_mean():
    start = pd.Timestamp(2016, 1, 15)
    end = pd.Timestamp(2016, 12, 15)
    arg = (ts_as_data_frame, ts_as_series)
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a[start:end], "M", agg="mean")
        # first mont (01/2016) and last month (2016/12) are incomplete.
        # 12 monts are available in 2016 when resampling using mean.
        assert len(ts_resampled) == 12
        assert str(ts_resampled.index[0]) == str(pd.Timestamp(2016, 1, 1))
        if i == 0:
            assert ts_resampled.iloc[0, 0] == ts_resampled.iloc[-1, 0] == 1
            assert ts_resampled.iloc[0, 1] == ts_resampled.iloc[-1, 1] == 2
        else:
            assert ts_resampled.iloc[0] == ts_resampled.iloc[-1] == 1


def test_monthly_resampling_incomplete_and_time_shift_mean():
    start = pd.Timestamp(2016, 1, 15, 18)
    end = pd.Timestamp(2016, 6, 30, 18)
    arg = (
        ts_as_data_frame[start:end].tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series[start:end].tz_localize("UTC").tz_convert("ETC/GMT-8"),
    )
    for i, a in enumerate(arg):
        ts_resampled = resample_time_series(a, "M", agg="mean")
        assert len(a) != len(ts_resampled)
        if i == 0:
            # first month (2016/01) and last month (2016/06) are incomplete.
            # 6 months are available in 2016 after resampling using mean.
            assert len(ts_resampled) == 6
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT+8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-06-01", tz="ETC/GMT+8")
            )
        else:
            # first month (2016/01) and last month (2016/07) are incomplete.
            # 6 months are available in Jamuary 2016 after resampling using mean.
            assert len(ts_resampled) == 6
            assert str(ts_resampled.index[0]) == str(
                pd.Timestamp("2016-01-01", tz="ETC/GMT-8")
            )
            assert str(ts_resampled.index[-1]) == str(
                pd.Timestamp("2016-06-01", tz="ETC/GMT-8")
            )


def test_change_time_zone_argument_type():
    arg = (
        (ts_as_series, 1),
        (ts_as_data_frame, {1, 2, 3}),
        (ts_as_series.to_dict(), "US/Eastern"),
    )
    for a in arg:
        with pytest.raises(TypeError):
            change_time_zone(a[0], a[1])


def test_change_time_zone_argument_value():
    arg = (
        (ts_as_data_frame, "US/Japan"),
        (ts_as_series.resample("D").sum(), "GMT+8"),
    )
    for a in arg:
        with pytest.raises(ValueError):
            change_time_zone(a[0], a[1])


def test_change_time_zone():
    arg = (ts_as_data_frame, ts_as_series)
    for a in arg:
        ts_idx = change_time_zone(a, "US/Pacific").index
        assert ts_idx.tz != pytz.timezone("UTC")
        assert ts_idx.tz == pytz.timezone("US/Pacific")
        assert set(ts_idx.year.unique()) == {2015, 2016}

        # assign time zone before calling function
        ts_idx = change_time_zone(a.tz_localize("UTC"), "US/Pacific").index
        assert ts_idx.tz != pytz.timezone("UTC")
        assert ts_idx.tz == pytz.timezone("US/Pacific")
        assert set(ts_idx.year.unique()) == {2015, 2016}


def test_is_dst():
    arg = (
        ts_as_data_frame.tz_localize("UTC").tz_convert("ETC/GMT+8"),
        ts_as_series.tz_localize("UTC"),
        ts_as_data_frame,
        ts_as_data_frame.tz_localize("UTC").tz_convert("US/Pacific"),
    )
    for i, a in enumerate(arg):
        if i < 3:
            assert not is_dst(a)
        else:
            assert is_dst(a)