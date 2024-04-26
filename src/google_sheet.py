import gspread

# If modifying the scopes, delete the token.json file to retrigger oauth
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


# #### Unusued functions

# COMMENT_FIELDS = "id, anchor, content, modifiedTime, quotedFileContent, author(displayName), replies(id,content,modifiedTime, author(displayName)), createdTime, htmlContent, kind, deleted, resolved"
# SPREADSHEET_ID = "18_0zVG1l3-HIhPwvSuONZxqwrjOCRN2JYhiiByi06_s"
# RANGE = "Sheet1!D7"

# def get_comments(drive_service):
#     comments_data = (
#         drive_service.comments()
#         .get(fileId=SPREADSHEET_ID, commentId="AAABLNjT_20", fields=COMMENT_FIELDS)
#         .execute()
#     )
#     return comments_data


# def add_comment(drive_service):
#     """
#     Comments attached to cell: https://www.youtube.com/live/ZBU52nacbLw?si=MTud8YGjvy1WFKxG&t=325
#     """
#     reply = (
#         drive_service.replies()
#         .create(
#             fileId=SPREADSHEET_ID,
#             commentId="AAABLNjT_20",
#             body=dict(kind="drive#reply", content="I am the content"),
#             fields="id, content, modifiedTime",
#         )
#         .execute()
#     )
#     return reply


# def create_note(sheets_service):
#     body = {
#         "requests": [
#             {
#                 "repeatCell": {
#                     "range": {
#                         "sheetId": 0,  # this is the end bit of the url
#                         "startRowIndex": 0,
#                         "endRowIndex": 1,
#                         "startColumnIndex": 0,
#                         "endColumnIndex": 1,
#                     },
#                     "cell": {"note": "Hey, I'm a comment!"},
#                     "fields": "note",
#                 }
#             }
#         ]
#     }
#     result = (
#         sheets_service.spreadsheets()
#         .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
#         .execute()
#     )
#     return result


# def increment_cell(service):
#     # Call the Sheets API
#     sheet = service.spreadsheets()
#     result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
#     values = result.get("values", [])

#     # Remove commas from the value
#     clean_value = values[0][0].replace(",", "") if values else "0"

#     # Increment the value by 1
#     new_value = int(clean_value) + 1

#     # Update cell D7 with the new value
#     body = {"values": [[new_value]]}
#     result = (
#         service.spreadsheets()
#         .values()
#         .update(
#             spreadsheetId=SPREADSHEET_ID,
#             range=RANGE,
#             valueInputOption="USER_ENTERED",
#             body=body,
#         )
#         .execute()
#     )


# def update_cell(service, new_value):
#     body = {"values": [[new_value]]}
#     result = (
#         service.spreadsheets()
#         .values()
#         .update(
#             spreadsheetId=SPREADSHEET_ID,
#             range=RANGE,
#             valueInputOption="USER_ENTERED",
#             body=body,
#         )
#         .execute()
#     )
#     print(f"result: {result}")


# def update_note(service, new_note, prev_note):
#     request = service.spreadsheets().batchUpdate(
#         spreadsheetId=SPREADSHEET_ID,
#         body={
#             "requests": [
#                 {
#                     "updateCells": {
#                         "range": {
#                             "sheetId": 0,  # Assuming the sheet ID is 0
#                             "startRowIndex": 6,  # 0-based, so 6 is row 7
#                             "endRowIndex": 7,
#                             "startColumnIndex": 3,  # 0-based, so 3 is column D
#                             "endColumnIndex": 4,
#                         },
#                         "rows": [{"values": [{"note": prev_note + "\n" + new_note}]}],
#                         "fields": "note",
#                     }
#                 }
#             ]
#         },
#     )
#     response = request.execute()
#     return response
