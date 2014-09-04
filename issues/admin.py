from django.contrib import admin
from issues.models import Issue, LocationRelation, Street

# Register your models here.

admin.site.register(Issue)
admin.site.register(LocationRelation)
admin.site.register(Street)
