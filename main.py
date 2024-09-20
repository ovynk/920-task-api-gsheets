from flask import Flask, request

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import retrieve_currency


app = Flask(__name__)

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def connect_to_xlsx(credentials_service_account_json, xlsx_name):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        keyfile_dict=credentials_service_account_json,
        scopes=scope
    )

    client = gspread.authorize(credentials)
    sheets = client.open(xlsx_name)

    return sheets


@app.route('/currency', methods=["PATCH"])
def currency():
    update_from = request.args.get('update_from')
    update_to = request.args.get('update_to')
    valcode = request.args.get('valcode')

    from_cell = request.args.get('from_cell')
    to_cell = request.args.get('to_cell')

    xlsx_name = request.args.get('xlsx_name')
    worksheet_id = request.args.get('worksheet_id')

    if valcode is None or \
            from_cell is None or \
            to_cell is None or \
            worksheet_id is None or \
            xlsx_name is None:
        return "Something is missing in url parameters. " \
               "(valcode, from_cell, to_cell, worksheet_id, xlsx_name)", 400

    # connect to file and a sheet
    # (there is only google api credentials in body)
    body = request.get_json()
    sheets = connect_to_xlsx(body, xlsx_name)
    worksheet = sheets.get_worksheet_by_id(worksheet_id)

    retrieved_bank_api = retrieve_currency.retrieve_currency(update_from, update_to, valcode)

    list_rates = [day['rate_per_unit'] for day in retrieved_bank_api]
    cell_list = worksheet.range(from_cell + ':' + to_cell)

    zipped_cell_value = zip(cell_list, list_rates)

    for cell, value in zipped_cell_value:
        cell.value = value

    worksheet.update_cells(cell_list)

    return "See", 200


@app.errorhandler(Exception)
def handle_bad_request(e):
    if len(e.args) == 0:
        return 'Error', 400

    return 'Error. ' + str(e), 400


if __name__ == '__main__':
    app.run(debug=True)
