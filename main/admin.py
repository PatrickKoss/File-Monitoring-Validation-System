from django.contrib import admin
from .models import CC050, CI050, MarginClass, ErrorRecipients


admin.site.register(CI050)
admin.site.register(CC050)
admin.site.register(MarginClass)
admin.site.register(ErrorRecipients)
