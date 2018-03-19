import hashlib
import zipfile

import requests
from django.utils.dateparse import parse_datetime
from urllib3.exceptions import MaxRetryError

from marer import consts


def parse_date_to_frontend_format(src_date_raw):
    return parse_datetime(src_date_raw).strftime('%d.%m.%Y')


def get_tender_info(gos_number):
    tdata = {}
    tender_data = {}

    if gos_number.startswith('http://zakupki.gov.ru/'):
        gos_number = gos_number.split('=', 1)[1]

    try:
        if len(gos_number) == 19:
            req = requests.get('http://cbcom.ru:8080/tender44?gosNumber=' + gos_number, timeout=3)
            if req and req.status_code != 200:
                return None
            if req.text:
                tdata = req.json()

            lot_data = tdata.get('lot', None)
            if not lot_data:
                lots = lot_data.get('lots', [])
                if len(lots) > 0:
                    lot_data = lots[0]

            requirements = lot_data.get('customerRequirements', [])
            cust_req_data = {}
            if len(requirements) > 0:
                cust_req_data = requirements[0]

            collecting_data = tdata.get('procedureInfo', {}).get('collecting', {})
            if len(collecting_data) == 0:
                collecting_data = None

            if tdata.get('purchaseResponsible', {}).get('responsibleRole', '') == 'CU':
                publisher = dict(
                    full_name=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('fullName'),
                    legal_address=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('factAddress'),
                    inn=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('inn'),
                    kpp=tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('kpp'),
                )
                beneficiary_reg_number = tdata.get('purchaseResponsible', {}).get('responsibleOrg', {}).get('regNum')
            else:
                publisher = dict()
                beneficiary_reg_number = cust_req_data.get('customer', {}).get('regNum')

            req = requests.get('http://cbcom.ru:8080/tender44org?regNumber=' + beneficiary_reg_number, timeout=3)
            if req and req.status_code != 200:
                pass
            if req.text:
                bdata = req.json()

                publisher_additional = dict(
                    full_name=bdata.get('fullName'),
                    legal_address=bdata.get('postalAddress'),
                    ogrn=bdata.get('ogrn'),
                    inn=bdata.get('inn'),
                    kpp=bdata.get('kpp'),
                )
                publisher.update(publisher_additional)

            tender_data = dict(
                gos_number=tdata.get('gosNumber'),
                law=consts.TENDER_EXEC_LAW_44_FZ,
                description=tdata.get('purchaseObjectInfo'),
                placement_type=tdata.get('placingWay', {}).get('name'),
                publish_date=parse_date_to_frontend_format(tdata.get('publishDate')),
                collect_start_date=parse_date_to_frontend_format(collecting_data.get('startDate')) if collecting_data else None,
                collect_end_date=parse_date_to_frontend_format(collecting_data.get('endDate')) if collecting_data else None,
                finish_date=None,
                start_cost=lot_data.get('maxPrice'),
                application_ensure_cost=cust_req_data.get('applicationGuarantee', {}).get('amount',
                                                                                          None) if cust_req_data.get(
                    'applicationGuarantee', None) else None,
                contract_execution_ensure_cost=cust_req_data.get('contractGuarantee', {}).get('amount',
                                                                                              None) if cust_req_data.get(
                    'contractGuarantee', None) else None,
                currency_code=consts.CURRENCY_RUR,
                publisher=publisher,
            )

        elif len(gos_number) == 11:
            req = requests.get('http://cbcom.ru:8080/tender223?gosNumber=' + gos_number, timeout=3)
            if req and req.status_code != 200:
                return None
            if req.text:
                tdata = req.json()

            publisher = dict(
                full_name=tdata.get('customer', {}).get('mainInfo', {}).get('fullName', ''),
                legal_address=tdata.get('customer', {}).get('mainInfo', {}).get('fullName', ''),
                ogrn=tdata.get('customer', {}).get('mainInfo', {}).get('ogrn', ''),
                inn=tdata.get('customer', {}).get('mainInfo', {}).get('inn', ''),
                kpp=tdata.get('customer', {}).get('mainInfo', {}).get('kpp', ''),
            )

            tender_data = dict(
                gos_number=tdata.get('purchaseNumber'),
                law=consts.TENDER_EXEC_LAW_223_FZ,
                description=tdata.get('purchaseObjectInfo'),
                placement_type=tdata.get('placingWayName'),
                publish_date=parse_date_to_frontend_format(tdata.get('publishDate')),
                collect_start_date=None,
                collect_end_date=None,
                finish_date=None,
                start_cost=tdata.get('lots', [])[0].get('lotData', {}).get('initialSum'),
                application_ensure_cost=None,
                contract_execution_ensure_cost=None,
                currency_code=consts.CURRENCY_RUR,
                publisher=publisher,
            )

    except MaxRetryError:
        pass

    return tender_data


def are_docx_files_identical(zip1_path: str, zip2_path: str) -> bool:
    zip1 = zipfile.ZipFile(zip1_path)
    zip2 = zipfile.ZipFile(zip2_path)

    def _check_zip_filelist_for_identity(z1, z2):
        fnames_z1 = [z.filename for z in z1.filelist]
        fnames_z2 = [z.filename for z in z2.filelist]
        for fname in fnames_z1:
            if str(fname).endswith('.rels'):
                continue
            if fname not in fnames_z2:
                return False
            zfile1 = z1.read(fname)
            zfile2 = z2.read(fname)
            md5_1 = hashlib.md5(zfile1).hexdigest()
            md5_2 = hashlib.md5(zfile2).hexdigest()
            if md5_1 != md5_2:
                return False
        return True

    check_z1_z2 = _check_zip_filelist_for_identity(zip1, zip2)
    check_z2_z1 = _check_zip_filelist_for_identity(zip2, zip1)

    return check_z1_z2 and check_z2_z1


# TODO: нормальзировать форму
OKOPF_CATALOG = {
    '11000': 'Хозяйственное товарищество',
    '11051': 'Полное товарищество',
    '11064': 'Товарищество на вере (коммандитное товарищество)',
    '12000': 'Хозяйственное общество',
    '12200': 'Акционерное общество',
    '12247': 'Публичное акционерное общество',
    '12267': 'Непубличное акционерное общество',
    '12300': 'общество с ограниченной ответственностью',
    '13000': 'Хозяйственное партнерство',
    '14000': 'Производственный кооператив',
    '14100': 'Сельскохозяйственный производственный кооперативы',
    '14153': 'Сельскохозяйственный артель',
    '14154': 'Рыболовецкий артель',
    '14155': 'Кооперативное хозяйство (коопхозы)',
    '14200': 'Производственный кооператив (кроме сельскохозяйственных производственных кооперативов)',
    '15300': 'Крестьянское (фермерские) хозяйство',
    '19000': 'коммерческая организация',
    '20100': 'Потребительские кооперативы',
    '20101': 'Гаражный и гаражно-строительный кооператив',
    '20102': 'Жилищный или жилищно-строительный кооператив',
    '20103': 'Жилищный накопительный кооператив',
    '20104': 'Кредитный потребительские кооператив',
    '20105': 'Кредитный потребительский кооператив граждан',
    '20106': 'Кредитный кооператив второго уровня',
    '20107': 'Потребительские общество',
    '20108': 'общество взаимного страхования',
    '20109': 'Сельскохозяйственный потребительский перерабатывающий кооператив',
    '20110': 'Сельскохозяйственный потребительский сбытовой (торговый) кооператив',
    '20111': 'Сельскохозяйственный потребительский обслуживающий кооператив',
    '20112': 'Сельскохозяйственный потребительский снабженческий кооператив',
    '20113': 'Сельскохозяйственный потребительский садоводческий кооператив',
    '20114': 'Сельскохозяйственный потребительский огороднический кооператив',
    '20115': 'Сельскохозяйственный потребительский животноводческий кооператив',
    '20120': 'Садоводческие, огороднические или дачный потребительский кооператив',
    '20121': 'Фонды проката',
    '20200': 'Общественные организации',
    '20201': 'Политические партии',
    '20202': 'Профсоюзные организации',
    '20210': 'Общественные движения',
    '20211': 'Органы общественной самодеятельности',
    '20217': 'Территориальные общественные самоуправления',
    '20600': 'Ассоциации (союзы)',
    '20601': 'Ассоциации (союзы) экономического взаимодействия субъектов Российской Федерации',
    '20603': 'Советы муниципальных образований субъектов Российской Федерации',
    '20604': 'Союзы (ассоциации) кредитных кооперативов',
    '20605': 'Союзы (ассоциации) кооперативов',
    '20606': 'Союзы (ассоциации) общественных объединений',
    '20607': 'Союзы (ассоциации) общин малочисленных народов',
    '20608': 'Союзы потребительских обществ',
    '20609': 'Адвокатские палаты',
    '20610': 'Нотариальные палаты',
    '20611': 'Торгово-промышленные палаты',
    '20612': 'Объединения работодателей',
    '20613': 'Объединения фермерских хозяйств',
    '20614': 'Некоммерческие партнерства',
    '20615': 'Адвокатские бюро',
    '20616': 'Коллегии адвокатов',
    '20617': 'Садоводческие, огороднические или дачные некоммерческие партнерства',
    '20618': 'Ассоциации (союзы) садоводческих, огороднических и дачных некоммерческих объединений',
    '20619': 'Саморегулируемые организации',
    '20620': 'Объединения (ассоциации и союзы) благотворительных организаций',
    '20700': 'Товарищество собственников недвижимости',
    '20701': 'Садоводческие, огороднические или дачные некоммерческие Товарищество',
    '20716': 'Товарищество собственников жилья',
    '21100': 'Казачьи общество, внесенные в государственный реестр казачьих обществ в Российской Федерации',
    '21200': 'Общины коренных малочисленных народов Российской Федерации',
    '30001': 'Представительства юридических лиц',
    '30002': 'Филиалы юридических лиц',
    '30003': 'Обособленные подразделения юридических лиц',
    '30004': 'Структурные подразделения обособленных подразделений юридических лиц',
    '30005': 'Паевые инвестиционные фонды',
    '30006': 'Простые Товарищество',
    '30008': 'Районные суды, городские суды, межрайонные суды (районные суды)',
    '40001': 'Межправительственные международные организации',
    '40002': 'Неправительственные международные организации',
    '50000': 'ОРГАНИЗАЦИОННО-ПРАВОВЫЕ ФОРМЫ ДЛЯ ДЕЯТЕЛЬНОСТИ ГРАЖДАН (ФИЗИЧЕСКИХ ЛИЦ)',
    '50100': 'Организационно-правовые формы для коммерческой деятельности граждан',
    '50101': 'Главы крестьянских (фермерских) хозяйств',
    '50102': 'Индивидуальные предприниматели',
    '50200': 'Организационно-правовые формы для деятельности граждан, не отнесенной к предпринимательству',
    '50201': 'Адвокаты, учредившие адвокатский кабинет',
    '50202': 'Нотариусы, занимающиеся частной практикой',
    '65000': 'Унитарные предприятия',
    '65100': 'Унитарные предприятия, основанные на праве оперативного управления (казенные предприятия)',
    '65141': 'Федеральные казенные предприятия',
    '65142': 'Казенные предприятия субъектов Российской Федерации',
    '65143': 'Муниципальные казенные предприятия',
    '65200': 'Унитарные предприятия, основанные на праве хозяйственного ведения',
    '65241': 'Федеральные государственные унитарные предприятия',
    '65242': 'Государственные унитарные предприятия субъектов Российской Федерации',
    '65243': 'Муниципальное унитарное предприятие',
    '70400': 'Фонд',
    '70401': 'Благотворительный фонд',
    '70402': 'Негосударственный пенсионный фонд',
    '70403': 'Общественный фонд',
    '70404': 'Экологические фонд',
    '71400': 'Автономная некоммерческая организация',
    '71500': 'Религиозная организациия',
    '71600': 'Публично-правовая компания',
    '71601': 'Государственная корпорация',
    '71602': 'Государственная компания',
    '71610': 'Отделение иностранных некоммерческих неправительственных организаций',
    '75000': 'Учреждение',
    '75100': 'Учреждение, созданное Российской Федерацией',
    '75101': 'Федеральное государственное автономное учреждение',
    '75103': 'Федеральное государственное бюджетное учреждение',
    '75104': 'Федеральное государственное казенное учреждение',
    '75200': 'Учреждения, созданные субъектом Российской Федерации',
    '75201': 'Государственные автономные учреждения субъектов Российской Федерации',
    '75203': 'Государственные бюджетные учреждения субъектов Российской Федерации',
    '75204': 'Государственные казенные учреждения субъектов Российской Федерации',
    '75300': 'Государственные академии наук',
    '75400': 'Учреждения, созданные муниципальным образованием (муниципальные учреждения)',
    '75401': 'Муниципальные автономные учреждения',
    '75403': 'Муниципальные бюджетные учреждения',
    '75404': 'Муниципальные казенные учреждения',
    '75500': 'Частные учреждения',
    '75502': 'Благотворительные учреждения',
    '75505': 'Общественные учреждения ',
}
