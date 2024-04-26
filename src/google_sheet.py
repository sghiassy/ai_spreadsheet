import gspread

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.activity.readonly",
]


gc = gspread.service_account(filename="./credentials.json")


def get_worksheet(sheet_name):
    wks = gc.open("AI Doc").worksheet(sheet_name)
    return wks


def get_active_cells(worksheet):
    list_of_lists = worksheet.get_all_values()
    active_list = []
    for i, row in enumerate(list_of_lists, start=1):  # Rows are 1-indexed
        for j, cell in enumerate(row, start=1):  # Columns are 1-indexed
            if cell:  # If the cell is not blank
                column_letter = chr(j + 64)  # Convert column number to letter
                active_list.append((f"{column_letter}{i}", cell))
    return active_list
