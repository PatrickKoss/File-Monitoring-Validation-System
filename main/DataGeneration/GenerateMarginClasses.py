import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SASTest.settings')
django.setup()

from main.models import MarginClass


def generate_margin_classes():
    margin_classes = ['SPAN', 'IMSM', 'CESM', 'AMPO', 'AMEM', 'AMCU', 'AMWI', 'DMEM']
    for margin_class in margin_classes:
        model = MarginClass.objects.create(margin_class=margin_class)
        model.save()


if __name__ == '__main__':
    generate_margin_classes()
