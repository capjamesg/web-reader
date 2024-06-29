import datetime

def transform_date_to_day_name_date(date: str):
    return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f").strftime("%A, %B %d")