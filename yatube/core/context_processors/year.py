import datetime


def year(request):
    now_year = int(datetime.datetime.now().year)
    return {
        'year': now_year,
    }
