import datetime as dt
import re

MONTH_NAMES = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

MONTH_ABBRS = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

WEEKDAY_ABBRS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# %[flags][width]conversion
RE_DIRECTIVE = re.compile(r"%([-_0^#:]*)(\d*)([A-Za-z%])")


def ruby_strftime(date: dt.datetime, fmt: str) -> str:
    iso_year, iso_week, iso_weekday = date.isocalendar()
    hour12 = date.hour % 12 or 12
    weekday_idx = date.weekday()  # 0 = Monday, 6 = Sunday

    # Handle timezone abbreviation (%Z)
    tzname = date.tzname()
    if tzname and tzname[0] in "+-":
        tz_Z = ""
    else:
        tz_Z = tzname or ""

    # Handle timezone offset components (%z, %:z)
    if date.tzinfo is not None and date.utcoffset() is not None:
        total_seconds = int(date.utcoffset().total_seconds())  # type: ignore
        sign = "+" if total_seconds >= 0 else "-"
        abs_sec = abs(total_seconds)
        hh = abs_sec // 3600
        mm = (abs_sec % 3600) // 60
    else:
        sign, hh, mm = "+", 0, 0

    def format_match(match: re.Match[str]) -> str:
        flags, width_str, conversion = match.groups()

        if conversion == "%":
            return "%"

        no_pad = "-" in flags
        space_pad = "_" in flags
        zero_pad = "0" in flags
        upcase = "^" in flags
        change_case = "#" in flags

        def pad_num(val: int, default_width: int, default_pad_char: str) -> str:
            width = int(width_str) if width_str else default_width
            if no_pad:
                return str(val)
            pad_char = " " if space_pad else ("0" if zero_pad else default_pad_char)
            s = str(val)
            if len(s) < width:
                s = s.zfill(width) if pad_char == "0" else s.rjust(width, " ")
            return s

        if conversion == "d":
            res = pad_num(date.day, 2, "0")
        elif conversion == "e":
            res = pad_num(date.day, 2, " ")
        elif conversion == "m":
            res = pad_num(date.month, 2, "0")
        elif conversion == "Y":
            res = pad_num(date.year, 4, "0")
        elif conversion == "y":
            res = pad_num(date.year % 100, 2, "0")
        elif conversion == "C":
            res = pad_num(date.year // 100, 2, "0")
        elif conversion == "H":
            res = pad_num(date.hour, 2, "0")
        elif conversion == "k":
            res = pad_num(date.hour, 2, " ")
        elif conversion == "I":
            res = pad_num(hour12, 2, "0")
        elif conversion == "l":
            res = pad_num(hour12, 2, " ")
        elif conversion == "M":
            res = pad_num(date.minute, 2, "0")
        elif conversion == "S":
            res = pad_num(date.second, 2, "0")
        elif conversion == "j":
            res = pad_num(date.timetuple().tm_yday, 3, "0")
        elif conversion == "G":
            res = pad_num(iso_year, 4, "0")
        elif conversion == "g":
            res = pad_num(iso_year % 100, 2, "0")
        elif conversion == "V":
            res = pad_num(iso_week, 2, "0")
        elif conversion == "W":
            res = pad_num(int(date.strftime("%W")), 2, "0")
        elif conversion == "U":
            res = pad_num(int(date.strftime("%U")), 2, "0")
        elif conversion == "w":
            res = str((weekday_idx + 1) % 7)
        elif conversion == "u":
            res = str(iso_weekday)
        elif conversion == "s":
            res = str(int(date.timestamp()))
        elif conversion == "B":
            res = MONTH_NAMES[date.month]
        elif conversion in ("b", "h"):
            res = MONTH_ABBRS[date.month]
        elif conversion == "A":
            res = WEEKDAY_NAMES[weekday_idx]
        elif conversion == "a":
            res = WEEKDAY_ABBRS[weekday_idx]
        elif conversion == "P":
            res = "am" if date.hour < 12 else "pm"
        elif conversion == "p":
            res = "AM" if date.hour < 12 else "PM"
        elif conversion == "Z":
            res = tz_Z
        elif conversion == "z":
            if date.tzinfo is None or date.utcoffset() is None:
                res = ""
            elif ":" in flags:
                res = f"{sign}{hh:02d}:{mm:02d}"
            else:
                res = f"{sign}{hh:02d}{mm:02d}"
        elif conversion == "c":
            res = f"{WEEKDAY_ABBRS[weekday_idx]} {MONTH_ABBRS[date.month]} {date.day:2d} {date.hour:02d}:{date.minute:02d}:{date.second:02d} {date.year}"
        elif conversion in ("D", "x"):
            res = f"{date.month:02d}/{date.day:02d}/{date.year % 100:02d}"
        elif conversion == "F":
            res = f"{date.year:04d}-{date.month:02d}-{date.day:02d}"
        elif conversion == "R":
            res = f"{date.hour:02d}:{date.minute:02d}"
        elif conversion == "r":
            p_str = "AM" if date.hour < 12 else "PM"
            res = f"{hour12:02d}:{date.minute:02d}:{date.second:02d} {p_str}"
        elif conversion in ("T", "X"):
            res = f"{date.hour:02d}:{date.minute:02d}:{date.second:02d}"
        elif conversion == "v":
            res = f"{date.day:2d}-{MONTH_ABBRS[date.month]}-{date.year:04d}"
        elif conversion == "n":
            res = "\n"
        elif conversion == "t":
            res = "\t"
        else:
            return match.group(0)

        # Apply case modifiers
        if upcase:
            res = res.upper()
        elif change_case:
            res = res.lower() if res.isupper() else res.upper()

        return res

    return RE_DIRECTIVE.sub(format_match, fmt)
