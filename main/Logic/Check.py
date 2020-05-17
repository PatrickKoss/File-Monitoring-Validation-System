import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SASTest.settings')
django.setup()

import logging
import datetime
import xml.etree.cElementTree as ET
from main.models import CI050, CC050, ErrorRecipients, MarginClass
from dateutil import parser
from django.core.mail import send_mail


class Check:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.START_TIME = datetime.datetime.strptime("1 May 2020 9 0 0", '%d %b %Y %H %M %S')
        self.END_TIME = datetime.datetime.strptime("1 May 2020 17 0 0", '%d %b %Y %H %M %S')
        self.error_message = ''
        self.margin_classes = self.get_margin_classes()
        self.email_list = self.get_email_list()

    def check(self, date):
        '''Method check if xml files and db entries are correct'''
        # reset error message
        self.error_message = ''
        yesterday = date - datetime.timedelta(days=1)

        # booleans for checking if files and db entries is correct
        check_xml_files = False
        check_db_entries = False

        # check if necessary files exists
        if not self.check_necessary_files_exists(date, yesterday):
            send_mail('Error Checks in Reports and Database', self.error_message, 'system@gmail.com', self.email_list,
                      fail_silently=False)
        else:
            check_xml_files = True

        # check if db data exist
        if not self.check_necessary_db_data_exists(date, yesterday):
            send_mail('Error Checks in Reports and Database', self.error_message, 'system@gmail.com', self.email_list,
                      fail_silently=False)
        else:
            check_db_entries = True

        # init reports with random values because of scope. Reports will be list of dictionaries
        today_CI050, yesterday_CI050, yesterday_CC050 = 1, 2, 3
        if check_xml_files:
            # check if files are correct and get xml data
            today_CI050, yesterday_CI050, yesterday_CC050 = self.report_check(date, yesterday)

        today_DB_CI050, yesterday_DB_CI050, yesterday_DB_CC050 = 1, 2, 3
        if check_db_entries:
            # check if db entries are correct and get db data
            today_DB_CI050, yesterday_DB_CI050, yesterday_DB_CC050 = self.db_check(date, yesterday)

        # if xml files and db entries exist then check each other
        if check_db_entries and check_xml_files:
            # finally check if entries from reports exists in db and vice versa
            self.check_values_in_entity(today_CI050, yesterday_DB_CI050, date, yesterday, "Report CI050",
                                        "Database Table CI050",
                                        self.START_TIME,
                                        self.END_TIME)
            self.check_values_in_entity(today_CI050, yesterday_DB_CI050, date, yesterday, "Report CI050",
                                        "Database Table CI050",
                                        self.START_TIME,
                                        self.END_TIME)
            self.check_values_in_entity(today_CI050, yesterday_DB_CC050, date, yesterday, "Report CI050",
                                        "Database Table CC050",
                                        self.START_TIME,
                                        self.END_TIME)
            self.check_values_in_entity(yesterday_DB_CC050, today_CI050, yesterday, date, "Database Table CC050",
                                        "Report CI050",
                                        self.END_TIME,
                                        self.START_TIME)
            self.check_values_in_entity(today_DB_CI050, yesterday_CC050, date, yesterday, "Database Table CI050",
                                        "Report CC050",
                                        self.START_TIME,
                                        self.END_TIME)
            self.check_values_in_entity(yesterday_CC050, today_DB_CI050, yesterday, date, "Report CC050",
                                        "Database Table CI050",
                                        self.END_TIME,
                                        self.START_TIME)
            self.check_values_in_entity(yesterday_CI050, today_DB_CI050, yesterday, date, "Report CI050",
                                        "Database Table CC050",
                                        self.END_TIME,
                                        self.START_TIME)
            self.check_values_in_entity(today_DB_CI050, yesterday_CI050, date, yesterday, "Database Table CI050",
                                        "Report CI050",
                                        self.START_TIME,
                                        self.END_TIME)

        # after error logs created send an email to recipients or log if we check was successful
        if self.error_message == '':
            self.logger.info("Check has been passed successfully!")
        else:
            send_mail('Error Checks in Reports and Database', self.error_message, 'system@gmail.com', self.email_list,
                      fail_silently=False)

    def get_email_list(self):
        '''Method return a list of email addresses from the database'''
        email_list = []
        error_recipients = ErrorRecipients.objects.all()
        for recipient in error_recipients:
            email_list.append(recipient.email)
        return email_list

    def get_margin_classes(self):
        '''Method return a list of margin classes'''
        margin_classes = []
        margin_classes_db = MarginClass.objects.all()
        for margin_class in margin_classes_db:
            margin_classes.append(margin_class.margin_class)
        return margin_classes

    def check_necessary_files_exists(self, today, yesterday):
        '''Method check if todays CI050, yesterdays CI050 and yesterdays CC050 exists'''
        # check if yesterday and today reports exists to do a check
        if not self.check_files_exist_helper("CC050", yesterday):
            return False
        if not self.check_files_exist_helper("CI050", yesterday):
            return False
        if not self.check_files_exist_helper("CI050", today):
            return False
        return True

    def check_files_exist_helper(self, report, date):
        if not os.path.exists("../Reports/{}-{}-{}-{}.xml".format(report, date.day, date.month, date.year)):
            message = "The file {}-{}-{}-{}.xml does not exist to perform a check".format(report, date.day,
                                                                                             date.month,
                                                                                             date.year)
            self.logger.error(message)
            self.error_message += message + "\n"
            return False
        else:
            return True

    def report_check(self, today, yesterday):
        '''check reports and return list dictionaries for future checks'''

        # get today CI050 xml report data which are the first entries of today so when trading start
        today_CI050 = self.get_report_data(today, "CI050", self.START_TIME)
        # get yesterday CI050 xml report data which are last entries of yesterday so when traiding ends
        yesterday_CI050 = self.get_report_data(yesterday, "CI050", self.END_TIME)
        # get report data of CC050
        yesterday_CC050 = self.get_report_data(yesterday, "CC050", self.END_TIME)

        # check all possibilities for a check
        self.check_values_in_entity(today_CI050, yesterday_CI050, today, yesterday, "Report CI050", "Report CI050",
                                    self.START_TIME,
                                    self.END_TIME)
        self.check_values_in_entity(yesterday_CI050, today_CI050, yesterday, today, "Report CI050", "Report CI050",
                                    self.END_TIME,
                                    self.START_TIME)
        self.check_values_in_entity(today_CI050, yesterday_CC050, today, yesterday, "Report CI050", "Report CC050",
                                    self.START_TIME,
                                    self.END_TIME)
        self.check_values_in_entity(yesterday_CC050, today_CI050, yesterday, today, "Report CC050", "Report CI050",
                                    self.END_TIME,
                                    self.START_TIME)
        self.check_values_in_entity(yesterday_CC050, yesterday_CI050, yesterday, yesterday, "Report CC050",
                                    "Report CI050",
                                    self.END_TIME, self.END_TIME)
        self.check_values_in_entity(yesterday_CI050, yesterday_CC050, yesterday, yesterday, "Report CI050",
                                    "Report CC050",
                                    self.END_TIME, self.END_TIME)

        return today_CI050, yesterday_CI050, yesterday_CC050

    def get_report_data(self, date, report, time):
        '''read in the xml file and return a list of dictionarys with keys as attributes and values from xml are values to the keys'''
        tree = ET.parse("../Reports/{}-{}-{}-{}.xml".format(report, date.day, date.month, date.year))
        root = tree.getroot()
        entry_dict = {}
        # set up the data which will be a list of dictionaries
        data = []
        for entry in root:
            # check if report date is in the entry
            report_time = entry.find('Report_Date')
            if report_time is None:
                continue
            margin_class = entry.find('Margin_Class')
            if margin_class is None:
                continue
            margin_class = margin_class.text
            # check if the margin class of the entry is in the list of margin classes
            if margin_class not in self.margin_classes:
                continue
            report_time = report_time.text
            # convert the date string into a date object
            report_time = parser.parse(report_time)
            # put only the entries with a specific time into the data which will be the start time and end time of trading
            if report_time.hour == time.hour and report_time.minute == time.minute and report_time.second == time.second:
                for children in entry:
                    entry_dict.update({children.attrib['name']: children.text})
                data.append(entry_dict)
                entry_dict = {}
            else:
                continue
        return data

    def check_necessary_db_data_exists(self, today, yesterday):
        '''check if data exists in database'''
        copy_today = today.replace(hour=self.START_TIME.hour, minute=self.START_TIME.minute, second=0)
        copy_yesterday = yesterday.replace(hour=self.END_TIME.hour, minute=self.END_TIME.minute, second=0)

        # check if there are entries in the database which have the start time of today and the end time of yesterday
        if not self.check_db_data_helper(CI050, copy_today, "CI050"):
            return False
        if not self.check_db_data_helper(CC050, copy_yesterday, "CC050"):
            return False
        if not self.check_db_data_helper(CI050, copy_yesterday, "CI050"):
            return False
        return True

    def check_db_data_helper(self, entity, date, report):
        '''Method check if db entries are existing'''
        if not entity.objects.filter(report_date__range=[date, date]).exists():
            message = "The database entries for {}-{}-{}-{} at {}:{} o clock does not exist to perform a check".format(
                report,
                date.day,
                date.month,
                date.year,
                date.hour,
                date.minute)
            self.logger.error(message)
            self.error_message += message + "\n"
            return False
        else:
            return True

    def db_check(self, today, yesterday):
        '''check database and return list dictionaries for future checks'''
        copy_today = today.replace(hour=self.START_TIME.hour, minute=self.START_TIME.minute, second=0)
        copy_yesterday = yesterday.replace(hour=self.END_TIME.hour, minute=self.END_TIME.minute, second=0)

        # get the same data as in the reports
        # filter the db data to all valid margin classes and dates
        today_CI050 = self.get_db_data(CI050.objects.filter(report_date__range=[copy_today, copy_today],
                                                            margin_class__margin_class__in=self.margin_classes))
        yesterday_CI050 = self.get_db_data(CI050.objects.filter(report_date__range=[copy_yesterday, copy_yesterday],
                                                                margin_class__margin_class__in=self.margin_classes))
        yesterday_CC050 = self.get_db_data(CC050.objects.filter(report_date__range=[copy_yesterday, copy_yesterday],
                                                                margin_class__margin_class__in=self.margin_classes))

        # perform the necessary checks
        self.check_values_in_entity(today_CI050, yesterday_CC050, today, yesterday, "Database Table CI050",
                                    "Database Table CC050", self.START_TIME, self.END_TIME)
        self.check_values_in_entity(yesterday_CC050, today_CI050, yesterday, today, "Database Table CC050",
                                    "Database Table CI050", self.END_TIME, self.START_TIME)
        self.check_values_in_entity(today_CI050, yesterday_CI050, today, yesterday, "Database Table CI050",
                                    "Database Table CI050", self.START_TIME, self.END_TIME)
        self.check_values_in_entity(yesterday_CI050, today_CI050, yesterday, today, "Database Table CI050",
                                    "Database Table CI050", self.END_TIME, self.START_TIME)
        self.check_values_in_entity(yesterday_CI050, yesterday_CC050, yesterday, yesterday, "Database Table CI050",
                                    "Database Table CC050", self.END_TIME, self.END_TIME)
        self.check_values_in_entity(yesterday_CC050, yesterday_CI050, yesterday, yesterday, "Database Table CC050",
                                    "Database Table CI050", self.END_TIME, self.END_TIME)
        return today_CI050, yesterday_CI050, yesterday_CC050

    def get_db_data(self, db_entity):
        '''return a list of dictionaries with keys as database attributes and values as the values'''
        data = []
        for entry in db_entity:
            entry_dict = dict((field.name, field.value_to_string(entry)) for field in entry._meta.fields)
            data.append(entry_dict)

        return data

    def check_values_in_entity(self, entity1, entity2, date1, date2, entity_name1, entity_name2, time1, time2):
        '''Method check if the values from entity 1 are included in entity 2'''
        for index, e1 in enumerate(entity1):
            is_in_entity2 = False
            for e2 in entity2:
                if e1['clearing_member'] in e2.values() and e1['account'] in e2.values() and e1[
                    'margin_class'] in e2.values() and e1['margin'] in e2.values():
                    is_in_entity2 = True
            if not is_in_entity2:
                # create error message
                message = "{} on {}-{}-{} {}:{} Clearing_Member: {}, Account: {}, Margin_Class: {}, Margin: {}, Report_Date: {} is not included in {} on {}-{}-{} {}:{}".format(
                    entity_name1, date1.day, date1.month, date1.year, time1.hour, time1.minute,
                    e1['clearing_member'], e1['account'], e1['margin_class'], e1['margin'],
                    e1['report_date'], entity_name2, date2.day,
                    date2.month,
                    date2.year, time2.hour, time2.minute)
                self.logger.error(message)
                self.error_message += message + "\n"


if __name__ == '__main__':
    test_date = datetime.datetime.strptime("10 May 2020", '%d %b %Y')
    # pass date of CI050 Report from today
    checker = Check()
    checker.check(test_date)
