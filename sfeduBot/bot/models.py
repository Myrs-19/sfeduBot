from unicodedata import name
from django.urls import reverse
from django.db import models


class Table(models.Model):
    week = models.SmallIntegerField()
    day = models.SmallIntegerField()
    lesson_number = models.SmallIntegerField()

    subject = models.TextField(null=True)
    auditorium = models.TextField(null=True)
    teacher = models.TextField(null=True)
    
    id_chat = models.IntegerField() #параметр который передается при открытии страницы


class Deadline(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    context = models.TextField()
    deadline_time = models.DateTimeField()
    create_time = models.TimeField(auto_now_add=True)
    interval = models.TimeField()


class Editor(models.Model):
    id_ed = models.IntegerField(primary_key=True, default='0')
    name = models.TextField()
    surname = models.TextField()
    deadline = models.ForeignKey(Deadline, on_delete=models.CASCADE, null=True)


class TableEditor(models.Model):
    table = models.ForeignKey(Table, on_delete=models.DO_NOTHING)
    editor = models.ForeignKey(Editor, on_delete=models.DO_NOTHING)


class User(models.Model):
    id_vk = models.IntegerField()
    name = models.TextField()
    surname = models.TextField()
    domain = models.TextField()
    id_chat = models.IntegerField()