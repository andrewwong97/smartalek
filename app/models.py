from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


# Create your models here.

class Course(models.Model):
    number = models.CharField(max_length=10, blank=True)
    ID = models.CharField(max_length=6, blank=True)
    prerequisites = models.ManyToManyField("self")
    title = models.CharField(max_length=200, blank=True)

    instructors = ArrayField(models.CharField(max_length=100, blank=True), default=list())
    location = models.CharField(max_length=200, blank=True)
    credits = models.FloatField(default=0.0)
    level = models.CharField(max_length=200, blank=True)
    semester = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return self.number + " " + self.title


class SemesterTranscript(models.Model):
    courses = models.ManyToManyField("Course")
    semester = models.CharField(max_length=16, blank=True)

class CompleteTranscript(models.Model):
    semesters = models.ManyToManyField("SemesterTranscript")
