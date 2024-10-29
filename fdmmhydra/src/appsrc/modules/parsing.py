import re
import time
import datetime
import requests
from pytz import timezone
from flask import url_for, render_template
from typing import List

def recursive_update(d1:dict, d2:dict) -> None:
    """
    Recursively combines two dictionaries
    """
    for key, value in d2.items():
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            recursive_update(d1[key], value)
        else:
            d1[key] = value

def parse_post_request(
        req:requests.Request,
        keys:list,
        required:bool=True,
        to_lower:bool=False,
        strip_whitespace:bool=True
    ) -> dict:
    """
    Parses a post request
    Can be used to see if the request has all required keys,
    and to sanitize the inputs
    """
    ret = {}
    for k in keys:
        ret[k] = req.form.get(k)
        if required and ret[k] is None:
            raise ValueError("POST response missing required key")
        if ret[k]:
            if to_lower: ret[k] = ret[k].lower()
            if strip_whitespace: ret[k] = ret[k].strip()
    return ret

def localize(utc_datetime:datetime.datetime) -> datetime.datetime:
    """Localize to system timezone"""
    if not utc_datetime: return None
    return utc_datetime.replace(tzinfo=datetime.timezone.utc).astimezone()

def pretty_date(
        local_datetime: datetime.datetime,
        seconds: bool = False,
        minutes: bool = True,
        hours: bool = True,
        use24: bool=True,
        show_tz: bool=False
    ) -> str:
    """
    Template helper function to make dates look better
    """
    if not local_datetime: return None
    format_string = f"%m/%d/%y "
    if hours: format_string += f"%{'H' if use24 else 'I'}"
    if minutes: format_string += ":%M"
    if seconds: format_string += ":%S"
    if not use24: format_string += "%p"
    if show_tz: format_string += "%Z"
    t = local_datetime.strftime(format_string)
    if show_tz:
        t.replace(
            "Pacific Daylight Time", "PDT"
        ).replace(
            "Pacific Standard Time", "PST"
        )
    return t

def format_seconds(time_in_seconds:int)->str:
    """
    Formats an integer number of seconds to a nice H:MM:SS format
    """
    hours, remainder = divmod(time_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    out = ""
    if int(hours): out += f"{int(hours)}:"
    if int(hours) or int(minutes): out += f"{str(int(minutes)).zfill(2)}:"
    return out + f"{str(int(seconds)).zfill(2)}"

def calculate_elapsed_and_remaining_time(start_time:float, completed:int, total:int):
    start_time = float(start_time)
    completed = int(completed)
    total = int(total)
    if not completed: completed = 1
    time_per_item = (elapsed := time.time()-start_time) / completed
    remaining_time = time_per_item * (total-completed)
    return f"E - {format_seconds(elapsed)} | R - {format_seconds(remaining_time)}\n"

def get_tz_from_localization(local_tz:timezone) -> str:
    """
    Template helper function to get server's local tz
    """
    return (
        datetime.datetime.now()
        .replace(tzinfo=datetime.timezone.utc)
        .astimezone(local_tz)
    ).strftime("%Z")

def add_html_breaks(content:str, min_content_length:int=12) -> str:
    """
    Makes long strings with certain characters
    """
    if not content: return ""
    if len(content) >= min_content_length:
        for char in ("_", "-", "/", "::", "="):
            content = content.replace(char, f"{char}&#8203;")
        content = content.replace("<", "&lt").replace(">", "&gt;")
    return content

def format_bytes(size:int) -> str:
    """
    Nicely formats a byte count
    """
    for suffix in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024: break
        size /= 1024
    return "{:.2f} {}".format(size, suffix)

def stringify_float(val:float|int|str) -> str:
    """
    Limit a number to two points of 
    precision to fix a jinja bug
    """
    if not val: return ""
    return "{:.1f}".format(float(val))
