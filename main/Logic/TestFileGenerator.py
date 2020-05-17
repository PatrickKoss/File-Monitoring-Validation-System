import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SASTest.settings')
django.setup()

from main.models import MarginClass, CI050, CC050
import xml.etree.cElementTree as ET
import datetime
import random

ACCOUNTS = ["SchmidFinancials", "MayerTraders", "MuellerEnterprise"]
CLEARING_MEMBER = ["Schmid", "Mayer", "Mueller"]
START_TIME = datetime.datetime.strptime("1 May 2020 9 0 0", '%d %b %Y %H %M %S')
END_TIME = datetime.datetime.strptime("1 May 2020 17 0 0", '%d %b %Y %H %M %S')


def generate_correct_data(today):
    '''generate correct data by writing the same data in the xml files and the database'''
    today = today.replace(hour=START_TIME.hour, minute=START_TIME.minute, second=0)

    # set the root for the xml files
    root_CI050_today = ET.Element("root")
    root_CC050_yesterday = ET.Element("root")
    root_CI050_yesterday = ET.Element("root")

    # get margin classes as list
    margin_classes_db = MarginClass.objects.all()
    margin_classes = []
    for margin_class in margin_classes_db:
        margin_classes.append(margin_class.margin_class)

    yesterday = today - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=END_TIME.hour, minute=END_TIME.minute, second=0)

    today_CI050_data = []
    yesterday_CI050_data = []
    yesterday_CC050_data = []

    # generate data
    entry = {}
    for margin_class in margin_classes:
        for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
            entry.update({"clearing_member": clearing_member})
            entry.update({"account": account})
            entry.update({"margin_class": margin_class})
            entry.update({"margin": 100})
            entry.update({"report_date": today})
            entry.update({"report_time": today})
            today_CI050_data.append(entry)
            entry = {}

    entry = {}
    for margin_class in margin_classes:
        for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
            entry.update({"clearing_member": clearing_member})
            entry.update({"account": account})
            entry.update({"margin_class": margin_class})
            entry.update({"margin": 100})
            entry.update({"report_date": yesterday})
            entry.update({"report_time": yesterday})
            yesterday_CI050_data.append(entry)
            entry = {}

    entry = {}
    for margin_class in margin_classes:
        for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
            entry.update({"clearing_member": clearing_member})
            entry.update({"account": account})
            entry.update({"margin_class": margin_class})
            entry.update({"margin": 100})
            entry.update({"report_date": yesterday})
            yesterday_CC050_data.append(entry)
            entry = {}

    # generate xml files
    for data in today_CI050_data:
        entry = ET.SubElement(root_CI050_today, "entry")
        ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = data["clearing_member"]
        ET.SubElement(entry, "Account", name="account").text = data["account"]
        ET.SubElement(entry, "Margin_Class", name="margin_class").text = data["margin_class"]
        ET.SubElement(entry, "Margin", name="margin").text = str(data["margin"])
        ET.SubElement(entry, "Report_Date", name="report_date").text = str(data["report_date"])
        ET.SubElement(entry, "Report_Time", name="report_time").text = str(data["report_time"])

    for data in yesterday_CI050_data:
        entry = ET.SubElement(root_CI050_yesterday, "entry")
        ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = data["clearing_member"]
        ET.SubElement(entry, "Account", name="account").text = data["account"]
        ET.SubElement(entry, "Margin_Class", name="margin_class").text = data["margin_class"]
        ET.SubElement(entry, "Margin", name="margin").text = str(data["margin"])
        ET.SubElement(entry, "Report_Date", name="report_date").text = str(data["report_date"])
        ET.SubElement(entry, "Report_Time", name="report_time").text = str(data["report_time"])

    for data in yesterday_CC050_data:
        entry = ET.SubElement(root_CC050_yesterday, "entry")
        ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = data["clearing_member"]
        ET.SubElement(entry, "Account", name="account").text = data["account"]
        ET.SubElement(entry, "Margin_Class", name="margin_class").text = data["margin_class"]
        ET.SubElement(entry, "Margin", name="margin").text = str(data["margin"])
        ET.SubElement(entry, "Report_Date", name="report_date").text = str(data["report_date"])

    # save data in db
    for entity in [today_CI050_data, yesterday_CI050_data, yesterday_CC050_data]:
        for entry in entity:
            margin_class = MarginClass.objects.get(margin_class=entry['margin_class'])
            if 'report_time' in entry:
                objects = CI050.objects.filter(clearing_member=entry['clearing_member'], account=entry['account'],
                                            margin_class=margin_class, margin=int(entry['margin']),
                                            report_date=entry['report_date'],
                                            report_time=entry['report_time'])
                if not objects.exists():
                    model = CI050.objects.create(clearing_member=entry['clearing_member'], account=entry['account'],
                                                 margin_class=margin_class, margin=int(entry['margin']),
                                                 report_date=entry['report_date'],
                                                 report_time=entry['report_time'])
                    model.save()
            else:
                objects = CC050.objects.filter(clearing_member=entry['clearing_member'], account=entry['account'],
                                            margin_class=margin_class, margin=int(entry['margin']),
                                            report_date=entry['report_date'])
                if not objects.exists():
                    model = CC050.objects.create(clearing_member=entry['clearing_member'], account=entry['account'],
                                                 margin_class=margin_class, margin=int(entry['margin']),
                                                 report_date=entry['report_date'])
                    model.save()

    # save xml files
    tree = ET.ElementTree(root_CC050_yesterday)
    tree.write("../Reports/CC050-{}-{}-{}.xml".format(yesterday.day, yesterday.month, yesterday.year))
    tree = ET.ElementTree(root_CI050_yesterday)
    tree.write("../Reports/CI050-{}-{}-{}.xml".format(yesterday.day, yesterday.month, yesterday.year))
    tree = ET.ElementTree(root_CI050_today)
    tree.write("../Reports/CI050-{}-{}-{}.xml".format(today.day, today.month, today.year))


def generate_false_data(today):
    '''generate false data by writing a different margin in type of xml reports while the others have the same data'''
    today = today.replace(hour=START_TIME.hour, minute=START_TIME.minute, second=0)

    # set the root for the xml files
    root_CI050_today = ET.Element("root")
    root_CC050_yesterday = ET.Element("root")
    root_CI050_yesterday = ET.Element("root")

    # get margin classes as list
    margin_classes_db = MarginClass.objects.all()
    margin_classes = []
    for margin_class in margin_classes_db:
        margin_classes.append(margin_class.margin_class)

    yesterday = today - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=END_TIME.hour, minute=END_TIME.minute, second=0)

    # store the data in a list of dictionaries
    today_CI050_data = []
    yesterday_CI050_data = []
    yesterday_CC050_data = []

    # generate data
    entry = {}
    for margin_class in margin_classes:
        for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
            entry.update({"clearing_member": clearing_member})
            entry.update({"account": account})
            entry.update({"margin_class": margin_class})
            entry.update({"margin": 100})
            entry.update({"report_date": today})
            entry.update({"report_time": today})
            today_CI050_data.append(entry)
            entry = {}

    entry = {}
    for margin_class in margin_classes:
        for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
            entry.update({"clearing_member": clearing_member})
            entry.update({"account": account})
            entry.update({"margin_class": margin_class})
            entry.update({"margin": 100})
            entry.update({"report_date": yesterday})
            entry.update({"report_time": yesterday})
            yesterday_CI050_data.append(entry)
            entry = {}

    entry = {}
    for margin_class in margin_classes:
        for account, clearing_member in zip(ACCOUNTS, CLEARING_MEMBER):
            entry.update({"clearing_member": clearing_member})
            entry.update({"account": account})
            entry.update({"margin_class": margin_class})
            entry.update({"margin": 100})
            entry.update({"report_date": yesterday})
            yesterday_CC050_data.append(entry)
            entry = {}

    # generate xml files
    for data in today_CI050_data:
        entry = ET.SubElement(root_CI050_today, "entry")
        ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = data["clearing_member"]
        ET.SubElement(entry, "Account", name="account").text = data["account"]
        ET.SubElement(entry, "Margin_Class", name="margin_class").text = data["margin_class"]
        ET.SubElement(entry, "Margin", name="margin").text = str(data["margin"])
        ET.SubElement(entry, "Report_Date", name="report_date").text = str(data["report_date"])
        ET.SubElement(entry, "Report_Time", name="report_time").text = str(data["report_time"])

    for data in yesterday_CI050_data:
        entry = ET.SubElement(root_CI050_yesterday, "entry")
        ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = data["clearing_member"]
        ET.SubElement(entry, "Account", name="account").text = data["account"]
        ET.SubElement(entry, "Margin_Class", name="margin_class").text = data["margin_class"]
        ET.SubElement(entry, "Margin", name="margin").text = str(data["margin"])
        ET.SubElement(entry, "Report_Date", name="report_date").text = str(data["report_date"])
        ET.SubElement(entry, "Report_Time", name="report_time").text = str(data["report_time"])

    for data in yesterday_CC050_data:
        entry = ET.SubElement(root_CC050_yesterday, "entry")
        ET.SubElement(entry, "Clearing_Member", name="clearing_member").text = data["clearing_member"]
        ET.SubElement(entry, "Account", name="account").text = data["account"]
        ET.SubElement(entry, "Margin_Class", name="margin_class").text = data["margin_class"]
        ET.SubElement(entry, "Margin", name="margin").text = str(200)
        ET.SubElement(entry, "Report_Date", name="report_date").text = str(data["report_date"])

    # save data in db
    for entity in [today_CI050_data, yesterday_CI050_data, yesterday_CC050_data]:
        for entry in entity:
            margin_class = MarginClass.objects.get(margin_class=entry['margin_class'])
            if 'report_time' in entry:
                objects = CI050.objects.filter(clearing_member=entry['clearing_member'], account=entry['account'],
                                            margin_class=margin_class, margin=int(entry['margin']),
                                            report_date=entry['report_date'],
                                            report_time=entry['report_time'])
                if not objects.exists():
                    model = CI050.objects.create(clearing_member=entry['clearing_member'], account=entry['account'],
                                                 margin_class=margin_class, margin=int(entry['margin']),
                                                 report_date=entry['report_date'],
                                                 report_time=entry['report_time'])
                    model.save()
            else:
                objects = CC050.objects.filter(clearing_member=entry['clearing_member'], account=entry['account'],
                                            margin_class=margin_class, margin=int(entry['margin']),
                                            report_date=entry['report_date'])
                if not objects.exists():
                    model = CC050.objects.create(clearing_member=entry['clearing_member'], account=entry['account'],
                                                 margin_class=margin_class, margin=int(entry['margin']),
                                                 report_date=entry['report_date'])
                    model.save()

    # save xml files
    tree = ET.ElementTree(root_CC050_yesterday)
    tree.write("../Reports/CC050-{}-{}-{}.xml".format(yesterday.day, yesterday.month, yesterday.year))
    tree = ET.ElementTree(root_CI050_yesterday)
    tree.write("../Reports/CI050-{}-{}-{}.xml".format(yesterday.day, yesterday.month, yesterday.year))
    tree = ET.ElementTree(root_CI050_today)
    tree.write("../Reports/CI050-{}-{}-{}.xml".format(today.day, today.month, today.year))


if __name__ == '__main__':
    date = datetime.datetime.strptime("16 May 2020", '%d %b %Y')
    # generate_correct_data(date)
    generate_false_data(date)
