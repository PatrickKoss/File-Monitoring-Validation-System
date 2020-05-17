import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SASTest.settings')
django.setup()

from main.models import MarginClass
import xml.etree.cElementTree as ET
import datetime
import random

ACCOUNTS = ["SchmidFinancials", "MayerTraders", "MuellerEnterprise"]
CLEARING_MEMBER = ["Schmid", "Mayer", "Mueller"]


def generate_date_list(date):
    base = date.replace(hour=9, minute=0, day=date.day, month=date.month, year=date.year)
    return [base + datetime.timedelta(seconds=x) for x in range(0, 8 * 60 * 60 + 10, 10)]


def generate_xml_files(start_date, days):
    root = ET.Element("root")
    root_CC050 = ET.Element("root")

    # generate a date list
    date_list = []
    date_list_CC050 = []
    date = datetime.datetime.strptime(start_date, '%d %b %Y')
    for addDay in range(days):
        date_list_CC050.append(date.replace(hour=17, minute=0))
        date_list.append(generate_date_list(date))
        date += datetime.timedelta(days=1)

    # get margin classes as list
    margin_classes_db = MarginClass.objects.all()
    margin_classes = []
    for margin_class in margin_classes_db:
        margin_classes.append(margin_class.margin_class)
    margin_class_samples = random.sample(margin_classes, random.randrange(0, len(margin_classes) - 1, 1))

    for index, dates in enumerate(date_list):
        for date in dates:
            for margin_class in margin_class_samples:
                for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
                    entry = ET.SubElement(root, "entry")
                    ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = clearing_member
                    ET.SubElement(entry, "Account", name="account").text = account
                    ET.SubElement(entry, "Margin_Class", name="margin_class").text = margin_class
                    ET.SubElement(entry, "Margin", name="margin").text = str(random.randrange(-500, 500, 50))
                    ET.SubElement(entry, "Report_Date", name="report_date").text = str(date)
                    ET.SubElement(entry, "Report_Time", name="report_time").text = str(date)
        tree = ET.ElementTree(root)
        tree.write("../Reports/CI050-{}-{}-{}.xml".format(dates[index].day, dates[index].month, dates[index].year))
        root = ET.Element("root")

    for date in date_list_CC050:
        for margin_class in margin_class_samples:
            for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
                entry = ET.SubElement(root_CC050, "entry")
                ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = clearing_member
                ET.SubElement(entry, "Account", name="account").text = account
                ET.SubElement(entry, "Margin_Class", name="margin_class").text = margin_class
                ET.SubElement(entry, "Margin", name="margin").text = str(random.randrange(-500, 500, 50))
                ET.SubElement(entry, "Report_Date", name="report_date").text = str(date)
        tree = ET.ElementTree(root_CC050)
        tree.write("../Reports/CC050-{}-{}-{}.xml".format(date.day, date.month, date.year))
        root_CC050 = ET.Element("root")


if __name__ == '__main__':
    generate_xml_files("01 May 2020", 6)
