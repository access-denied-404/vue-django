from io import BytesIO
from string import Formatter

from django.core.files.base import ContentFile
from docx import Document
from docx.text.paragraph import Paragraph
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


def _fill_docx_paragraph_with_dict(paragraph: Paragraph, data: dict) -> None:
    runs = paragraph.runs

    paragraph_params = Formatter().parse(paragraph.text)
    paragraph_params = [pp for pp in paragraph_params if pp[1] is not None]
    if len(paragraph_params) == 0:
        return

    for run in runs[:-1]:
        curr_idx = runs.index(run)
        next_run = runs[curr_idx + 1]
        open_brace_last_pos = str(run.text).rfind('{')
        close_brace_last_pos = str(run.text).rfind('}')

        if open_brace_last_pos > close_brace_last_pos:
            next_run.text = run.text[open_brace_last_pos:] + next_run.text
            run.text = run.text[:open_brace_last_pos]

    for run in runs:
        old_text = str(run.text)
        try:
            new_text = old_text.format(**data)
        except KeyError:
            pass
        except ValueError:
            pass
        else:
            if old_text != new_text:
                run.text = new_text


def fill_docx_file_with_issue_data(path: str, issue: Issue) -> ContentFile:
    self_data = issue.__dict__
    self_data['user'] = issue.user
    self_data['issue'] = issue

    doc = Document(path)
    for paragraph in doc.paragraphs:
        _fill_docx_paragraph_with_dict(paragraph, self_data)
    for table in doc.tables:
        rows_cnt = len(table.rows)
        for row_idx in range(0, rows_cnt):
            for cell in table.row_cells(row_idx):
                for p in cell.paragraphs:
                    _fill_docx_paragraph_with_dict(p, self_data)

    stream = BytesIO()
    doc.save(stream)

    stream.seek(0)
    cf = ContentFile(stream.read())
    return cf
