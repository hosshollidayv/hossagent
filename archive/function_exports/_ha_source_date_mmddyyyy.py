def _ha_source_date_mmddyyyy(days_back=365):
    end = date.today()
    start = end - timedelta(days=days_back)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")