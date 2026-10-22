import datetime as dt

import pytest

from liquid._strftime import ruby_strftime

DT = dt.datetime.fromisoformat("2026-10-17 18:27:00 -04:00")
DT_SINGLE_DIGITS = dt.datetime.fromisoformat("2026-01-05 04:05:06 +05:30")
DT_MIDNIGHT = dt.datetime(2026, 1, 1, 0, 0, 0)
DT_NOON = dt.datetime(2026, 1, 1, 12, 0, 0)


@pytest.mark.parametrize(
    "date,fmt,want",
    [
        pytest.param(DT, r"%s", "1792276020", id="unix_timestamp"),
        pytest.param(DT, r"%C", "20", id="century"),
        pytest.param(DT, r"%y", "26", id="two_digit_year"),
        pytest.param(DT, r"%Y", "2026", id="four_digit_year"),
        pytest.param(DT, r"%h", "Oct", id="abbreviated_month_alias"),
        pytest.param(DT, r"%e", "17", id="day_space_padded"),
        pytest.param(DT, r"%b", "Oct", id="abbreviated_month"),
        pytest.param(DT, r"%B", "October", id="full_month_name"),
        pytest.param(DT, r"%m", "10", id="month"),
        pytest.param(DT, r"%d", "17", id="day_two_digits"),
        pytest.param(DT, r"%w", "6", id="weekday_number"),
        pytest.param(DT, r"%u", "6", id="weekday_number_monday_start"),
        pytest.param(DT, r"%H", "18", id="hour_24"),
        pytest.param(DT, r"%I", "06", id="hour_12"),
        pytest.param(DT, r"%S", "00", id="second"),
        pytest.param(DT, r"%M", "27", id="minute"),
        pytest.param(DT, r"%l", " 6", id="hour_12_space_padded"),
        pytest.param(DT, r"%k", "18", id="hour_24_space_padded"),
        pytest.param(DT, r"%I", "06", id="hour_12_midnight"),
        pytest.param(DT, r"%a", "Sat", id="abbreviated_weekday"),
        pytest.param(DT, r"%A", "Saturday", id="full_weekday"),
        pytest.param(DT, r"%j", "290", id="day_of_year_january"),
        pytest.param(DT, r"%j", "290", id="day_of_year"),
        pytest.param(DT, r"%P", "pm", id="am_pm_lowercase"),
        pytest.param(DT, r"%p", "PM", id="AM_PM_uppercase"),
        pytest.param(DT, r"%g", "26", id="iso_week_year_2digit"),
        pytest.param(DT, r"%G", "2026", id="iso_week_year"),
        pytest.param(DT, r"%V", "42", id="iso_week"),
        pytest.param(DT, r"%W", "41", id="week_monday_start"),
        pytest.param(DT, r"%U", "41", id="week_sunday_start"),
        pytest.param(DT, r"%r", "06:27:00 PM", id="12h_time"),
        pytest.param(DT, r"%T", "18:27:00", id="24h_time_with_seconds"),
        pytest.param(DT, r"%R", "18:27", id="24h_time"),
        pytest.param(DT, r"%F", "2026-10-17", id="iso_date"),
        pytest.param(DT, r"%D", "10/17/26", id="short_date"),
        pytest.param(DT, r"%X", "18:27:00", id="preferred_time"),
        pytest.param(DT, r"%x", "10/17/26", id="preferred_date"),
        pytest.param(DT, r"%c", "Sat Oct 17 18:27:00 2026", id="preferred_datetime"),
        pytest.param(DT, r"%Z", "", id="timezone_name"),
        pytest.param(DT, r"%z", "-0400", id="timezone_offset"),
        pytest.param(DT, r"%:z", "-04:00", id="timezone_offset_colon"),
        pytest.param(DT, r"%-d", "17", id="dash_no_padding"),
        pytest.param(DT, r"%0d", "17", id="zero_padding"),
        pytest.param(DT, r"%#B", "OCTOBER", id="hash_opposite_case"),
        pytest.param(DT, r"%%", "%", id="literal_percent"),
        pytest.param(DT, r"%n", "\n", id="newline_character"),
        pytest.param(DT, r"%t", "\t", id="tab_character"),
        pytest.param(DT, r"%v", "17-Oct-2026", id="vms_date"),
        pytest.param(DT_SINGLE_DIGITS, r"%d", "05", id="single_digit_day_zero_padded"),
        pytest.param(DT_SINGLE_DIGITS, r"%e", " 5", id="single_digit_day_space_padded"),
        pytest.param(DT_SINGLE_DIGITS, r"%-d", "5", id="single_digit_day_no_padding"),
        pytest.param(
            DT_SINGLE_DIGITS, r"%m", "01", id="single_digit_month_zero_padded"
        ),
        pytest.param(DT_SINGLE_DIGITS, r"%-m", "1", id="single_digit_month_no_padding"),
        pytest.param(
            DT_SINGLE_DIGITS, r"%H", "04", id="single_digit_hour24_zero_padded"
        ),
        pytest.param(
            DT_SINGLE_DIGITS, r"%k", " 4", id="single_digit_hour24_space_padded"
        ),
        pytest.param(
            DT_SINGLE_DIGITS, r"%I", "04", id="single_digit_hour12_zero_padded"
        ),
        pytest.param(
            DT_SINGLE_DIGITS, r"%l", " 4", id="single_digit_hour12_space_padded"
        ),
        pytest.param(DT_SINGLE_DIGITS, r"%j", "005", id="single_digit_day_of_year"),
        pytest.param(DT_MIDNIGHT, r"%H", "00", id="midnight_hour24"),
        pytest.param(DT_MIDNIGHT, r"%I", "12", id="midnight_hour12"),
        pytest.param(DT_MIDNIGHT, r"%k", " 0", id="midnight_hour24_space_padded"),
        pytest.param(DT_MIDNIGHT, r"%l", "12", id="midnight_hour12_space_padded"),
        pytest.param(DT_MIDNIGHT, r"%P", "am", id="midnight_am"),
        pytest.param(DT_NOON, r"%H", "12", id="noon_hour24"),
        pytest.param(DT_NOON, r"%I", "12", id="noon_hour12"),
        pytest.param(DT_NOON, r"%k", "12", id="noon_hour24_space_padded"),
        pytest.param(DT_NOON, r"%l", "12", id="noon_hour12_space_padded"),
        pytest.param(DT_NOON, r"%P", "pm", id="noon_pm"),
        pytest.param(DT, r"%^b", "OCT", id="upcase_flag_month_abbr"),
        pytest.param(DT, r"%^A", "SATURDAY", id="upcase_flag_weekday_full"),
        pytest.param(DT, r"%#B", "OCTOBER", id="hash_flag_opposite_case_titlecase"),
        pytest.param(DT, r"%#p", "pm", id="hash_flag_opposite_case_uppercase"),
        pytest.param(DT_SINGLE_DIGITS, r"%_d", " 5", id="space_pad_flag"),
        pytest.param(DT, r"%10Y", "0000002026", id="custom_width_year"),
        pytest.param(DT_SINGLE_DIGITS, r"%3d", "005", id="custom_width_day"),
        pytest.param(DT_SINGLE_DIGITS, r"%z", "+0530", id="positive_tz_offset"),
        pytest.param(DT_SINGLE_DIGITS, r"%:z", "+05:30", id="positive_tz_offset_colon"),
        pytest.param(DT_MIDNIGHT, r"%z", "", id="naive_datetime_tz_offset"),
        pytest.param(DT_MIDNIGHT, r"%Z", "", id="naive_datetime_tz_name"),
    ],
)
def test_strftime(date: dt.datetime, fmt: str, want: str) -> None:
    assert ruby_strftime(date, fmt) == want
