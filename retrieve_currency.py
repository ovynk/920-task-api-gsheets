from datetime import date
import requests


current_date_formatted = date.today().strftime("%Y%m%d")


def retrieve_currency(start, end, valcode):
    start = current_date_formatted if start is None else start.replace('-', '')
    end = current_date_formatted if end is None else end.replace('-', '')

    url = f"https://bank.gov.ua/NBU_Exchange/exchange_site" \
          f"?start={start}&end={end}&valcode={valcode}&sort=exchangedate&order=asc&json"

    response = requests.get(url)
    return response.json()
