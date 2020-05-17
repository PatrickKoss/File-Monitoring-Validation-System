from django.db import models


class MarginClass(models.Model):
    margin_class = models.CharField(max_length=100, primary_key=True)


class ErrorRecipients(models.Model):
    first_name = models.CharField(max_length=100)
    sur_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)


class CI050(models.Model):
    clearing_member = models.CharField(max_length=100)
    account = models.CharField(max_length=100)
    margin_class = models.ForeignKey(MarginClass, default=1, verbose_name="MarginClass", on_delete=models.CASCADE)
    margin = models.IntegerField()
    report_date = models.DateTimeField()
    report_time = models.DateTimeField()


class CC050(models.Model):
    clearing_member = models.CharField(max_length=100)
    account = models.CharField(max_length=100)
    margin_class = models.ForeignKey(MarginClass, default=1, verbose_name="MarginClass", on_delete=models.CASCADE)
    margin = models.IntegerField()
    report_date = models.DateTimeField()
