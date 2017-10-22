import logging

from django.core.management.base import BaseCommand
from openpyxl import load_workbook

from marer.models.finance_org import FinanceOrgProductConditions
from marer.products import get_finance_products

logger = logging.getLogger('django')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('product', nargs=1, type=str)
        parser.add_argument('filename', nargs=1, type=str)
        parser.add_argument('sheet', nargs='?', type=str)

    def handle(self, *args, **options):

        product = None
        product_name = options.get('product')[0]
        for prod in get_finance_products():
            if prod.name == product_name or prod.name == product_name + 'Product':
                product = prod
                break

        filename = options.get('filename')[0]
        sheet_name = options.get('sheet', None)

        foc_list = FinanceOrgProductConditions.objects.filter(finance_product=product.name)
        for foc in foc_list:
            foc.delete()

        wb = load_workbook(filename)
        if sheet_name is not None:
            sh = wb.get_sheet_by_name(sheet_name)
        else:
            sheets = wb.get_sheet_names()
            sh = wb.get_sheet_by_name(sheets[0])

        product.load_finance_orgs_conditions_from_worksheet(sh)
