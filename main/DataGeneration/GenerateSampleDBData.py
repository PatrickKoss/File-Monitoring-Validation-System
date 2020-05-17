import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SASTest.settings')
django.setup()

from main.models import MarginClass, CI050, CC050
import xml.etree.cElementTree as ET
from dateutil import parser


def generate_DB_Data():
    data = []
    for path in os.listdir("../Reports"):
        tree = ET.parse(os.path.join("../Reports", path))
        root = tree.getroot()
        entry_dict = {}
        for entry in root:
            for children in entry:
                entry_dict.update({children.attrib['name']: children.text})
            data.append(entry_dict)
            entry_dict = {}

    for entry in data:
        margin_class = MarginClass.objects.get(margin_class=entry['margin_class'])
        if 'report_time' in entry:
            if not CI050.objects.filter(clearing_member=entry['clearing_member'], account=entry['account'],
                                        margin_class=margin_class, margin=int(entry['margin']),
                                        report_date=entry['report_date'],
                                        report_time=parser.parse(entry['report_time'])).exists():
                model = CI050.objects.create(clearing_member=entry['clearing_member'], account=entry['account'],
                                             margin_class=margin_class, margin=int(entry['margin']),
                                             report_date=parser.parse(entry['report_date']),
                                             report_time=parser.parse(entry['report_time']))
                model.save()
        else:
            if not CC050.objects.filter(clearing_member=entry['clearing_member'], account=entry['account'],
                                        margin_class=margin_class, margin=int(entry['margin']),
                                        report_date=parser.parse(entry['report_date'])).exists():
                model = CC050.objects.create(clearing_member=entry['clearing_member'], account=entry['account'],
                                             margin_class=margin_class, margin=int(entry['margin']),
                                             report_date=parser.parse(entry['report_date']))
                model.save()


if __name__ == '__main__':
    generate_DB_Data()
