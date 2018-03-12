import datetime

from django.utils import timezone

from dateutil.relativedelta import relativedelta


def get_datetime_as_excel_number(date, limit=7):
    now = date
    start_date = now.replace(minute=0, second=0, hour=0, microsecond=0)
    dt = now - timezone.make_aware(datetime.datetime(1899, 12, 31))
    return float('%s.%s' % (dt.days, str((now - start_date).seconds / (60 * 60 * 24)).split('.')[-1][:limit]))


def get_date_diff_in_days(start_date, end_date):
    return (end_date - start_date).days


def year():
    return datetime.datetime.now().year


def month():
    return datetime.datetime.now().strftime('%m')


def day():
    return datetime.datetime.now().strftime('%d')


def today():
    return datetime.datetime.now()


def month_difference_from_today(date):
    if date < today():
        return relativedelta(today(), date).months
    else:
        return relativedelta(date, today()).months
