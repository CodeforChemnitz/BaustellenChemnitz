from django.db import models

# Create your models here.


class LocationRelation(models.Model):

    relation = models.TextField()


class Issue(models.Model):
    street_name = models.TextField()

    restriction = models.TextField()
    action = models.TextField()

    since_date = models.DateField()
    until_date = models.DateField()
    date_notice = models.TextField()

    location_relation = models.ForeignKey(LocationRelation)


class Streets(models.Model):

    issue = models.ForeignKey(Issue)
    street_name = models.TextField()
