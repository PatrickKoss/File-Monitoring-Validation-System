# File-Monitoring-Validation-System
> A system that monitor file uploads and validates the files and database entries and vice versa. This system was created as part of a job interview.

## Structure
- The [main](./main/) app is responsible for all the logic.
- In [main/DataGeneration](./main/DataGeneration/) are scripts that create reports and database entries for initializing the system.
- In [main/Logs](./main/Logs/) is a debug file which reports validation success or errors.
- In [main/Reports](./main/Reports/) are reports in xml format. This dictionary is observed by a watcher that recognize if a new file is added.
- In [main/Logic](./main/Logic/) is the main logic for the system.
- [main/Logic/Check.py](./main/Logic/Check.py) is the validation script. It validates reports and database entries.
- [main/Logic/TestFileGenerator.py](./main/Logic/TestFileGenerator.py) generate test reports and database entries for testing the system.
- [main/Logic/Watcher.py](./main/Logic/Watcher.py) observe the Reports dictionary and trigger the Check.py check.

## Prerequisites and Usage

-   Install python 3.
-   Install pip.
-   Install all python modules by pip install -r requirements or install them by hand with pip install nameOfTheModule.
-   Make migrations to setup the database by `python manage.py migrate` and `python manage.py makemigrations`
-   run the watcher by `python ./main/Logic/Watcher.py`
-   check the system by simulating the system functionality with `python ./main/Logic/TestFileGenerator.py`


## Detailed Build Setup

```bash
# install dependencies
pip install -r requirements

# make migrations
python manage.py migrate
python manage.py makemigration

# run locally on 127.0.0.1
python manage.py runserver

# run the watcher
python ./main/Logic/Watcher.py
```

## System Purpose and Functionality
- Once the report CI050 of a date is uploaded to reports the first entries of a day of the report CI050 must be included in in the reports CC050 of yesterdays date and in the last entries in CI050 of yesterdays date. The next check is to check if the last entries of the report CC050 of yesterdays date must be included in the last entries of yesterdays date report of CI050. And vice versa.
- This check has to be performed for the database tables CC050 and CI050 as well and for the reports and database tables.
- The Watcher.py recognize if a report is uploaded in main/reports and triggers the check.
- If the check was not passed then an email is sent to a group of recipients which can be modified in the database table "Error Recipients" and an error log is written in main/Logs/debug.log.