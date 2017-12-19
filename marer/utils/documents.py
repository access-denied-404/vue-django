from django.core.files.base import ContentFile
from openpyxl import load_workbook
from openpyxl.writer.excel import save_virtual_workbook

from marer.models import Issue


def fill_xlsx_file_with_issue_data(path: str, issue: Issue) -> ContentFile:
    wb = load_workbook(path, keep_vba=True, guess_types=False)
    self_data = issue.__dict__
    self_data['user'] = issue.user
    self_data['issue'] = issue
    for ws_name in wb.sheetnames:
        ws = wb.get_sheet_by_name(ws_name)
        for cell in ws.get_cell_collection():
            if cell.value is not None:
                old_cell_value = str(cell.value)
                try:
                    new_cell_value = old_cell_value.format(**self_data)
                except KeyError:
                    new_cell_value = old_cell_value
                if new_cell_value != old_cell_value:
                    cell.value = new_cell_value
                cell.value = new_cell_value
    cf = ContentFile(save_virtual_workbook(wb))
    wb.close()
    return cf
