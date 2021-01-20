import pandas as pd
import pytz

from postreise.analyze.check import (
    _check_date_range_in_time_series,
    _check_time_series,
)


def slice_time_series(ts, start, end):
    """Slice a time series.

    :param pandas.DataFrame/pandas.Series ts: time series to slice.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime start: start date.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime end: end date.
    :return: (*pandas.DataFrame/pandas.Series*) -- the sliced time series.
    """
    _check_date_range_in_time_series(ts, start, end)

    return ts[start:end]


def resample_time_series(ts, freq, agg="sum"):
    """Resample a time series.

    :param pandas.DataFrame/pandas.Series ts: time series to resample.
    :param str freq: frequency. Either *'D'* (day), *'W'* (week), *'M'* (month).
    :param str agg: aggregation method. Either *'sum'* or *'mean'*.
    :return: (*pandas.DataFrame/pandas.Series*) -- the resampled time series.
    :raises ValueError: if freq is not one of *'D'*, *'W'*, *'M'* or agg is not one of
        *'sum'* or *'mean'* or ts is time zone aware with DST.

    .. note::
        When resampling:

        * the left side of the bin interval is closed.
        * the left bin edge is used to label the interval.
        * intervals start at midnight when freq is *'D'*.
        * intervals start on Sunday when freq is *'W'*.
        * incomplete days, weeks and months are clipped when agg is *'sum'*.
        * incomplete days, weeks and months are calculated using available data
          samples when agg is *'mean'*.
    """
    _check_time_series(ts, "time series")
    if is_dst(ts):
        raise ValueError(
            "DST is not supported. Use ETC/GMT+x or ETC/GMT-x where x is the offset"
        )

    if freq not in ["D", "W", "M"]:
        raise ValueError("frequency must be one of 'D', 'W', 'M'")

    if agg not in ["sum", "mean"]:
        raise ValueError("aggregation method must 'sum' or 'mean'")

    if agg == "sum":
        print("clip incomplete %s" % {"D": "days", "W": "weeks", "M": "months"}[freq])

    if freq == "D":
        if agg == "sum":
            return ts.resample("D").sum(min_count=24).dropna()
        else:
            return ts.resample("D").mean()
    elif freq == "W":
        if agg == "sum":
            return (
                ts.resample("W", label="left", closed="left")
                .sum(min_count=7 * 24)
                .dropna()
            )
        else:
            return ts.resample("W", label="left", closed="left").mean()
    elif freq == "M":
        if agg == "sum":
            # coerce Series to DataFrame as necessary, grab first column, count entries by month
            count = pd.DataFrame(ts).iloc[:, 0].resample("MS").count().to_dict()
            keep = [k for k, v in count.items() if k.days_in_month * 24 == v]
            return ts.resample("MS").sum().filter(items=keep, axis=0)
        else:
            return ts.resample("MS").mean()


def change_time_zone(ts, tz):
    """Convert hourly time series to new time zone. UTC is assumed if no time zone is
    assigned to the input time series.

    :param pandas.DataFrame/pands.Series ts: time series.
    :param str tz: new time zone.
    :return: (*pandas.DataFrame/pandas.Series*) -- time series with new time zone.
    :raises TypeError: if tz is not a str.
    :raises ValueError: if tz is invalid or the time series has already been resampled.
    """
    _check_time_series(ts, "time series")

    if pd.infer_freq(ts.index) != "H":
        raise ValueError("frequency of time series must be 1h")

    if not isinstance(tz, str):
        raise TypeError("time zone must be a str")
    try:
        pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError("Unknown time zone %s" % tz)

    if ts.index.tz is None:
        return ts.tz_localize("UTC").tz_convert(tz)
    else:
        return ts.tz_convert(tz)


def is_dst(ts):
    """Flag Daylight Saving Time (DST) in a time series.

    :param pandas.DataFrame/pands.Series ts: time series.
    :return: (*bool*) -- True if time zone observes DST.
    """
    if ts.index.tz is None:
        return False
    else:
        return ts.index.map(lambda x: x.dst().total_seconds() != 0).any()
