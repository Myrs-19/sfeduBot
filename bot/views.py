from typing import Dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from .models import *


def get_data(request) -> Dict:
    '''функция получения словаря для вывода расписания в форме'''
    if request.method == "GET":
        id_editor = request.GET['id_editor']
        id_chat = request.GET['id_chat']
        ed_name = request.GET['ed_name']
        ed_surname = request.GET['ed_surname']
    else:
        id_editor = request.POST['id_editor']
        id_chat = request.POST['id_chat']

    
    table = Table.objects.get_or_create(id_chat=id_chat, lesson_number=1, week=1, day=1)[0]
    if not Editor.objects.filter(id_ed=id_editor):
        # сюда мы заходим только тогда когда существует расписание
        # когда создается и староста, и расписание - ошибка
        editor = Editor.objects.create(
            id_ed=id_editor,
            name=ed_name,
            surname=ed_surname
        )
        TableEditor.objects.create(table=table, editor=editor)

    # словарь уроков, каждый подсловарь - день, ключ подсловаря - номер урока, значение подсловаря - данные: ПРЕДМЕТ, АУДИТОРИЯ, ПРЕПОД 
    data = {
        1 : {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        },
        2 : {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        },
        3 : {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        },
        4 : {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        },
        5 : {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        },
        6 : {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
        }
        
    }
    # проверка на существование расписания (таблицы)
    if table:
        # формирование объектов из бд для вывода расписания
        data = {}  # дни
        for i in range(1, 7):
            dd = {}  # номера уроков\пар
            for j in range(1, 8):

                dd[j] = [Table.objects.filter(day=i, lesson_number=j, week=1, id_chat=id_chat)[0] if Table.objects.filter(day=i, lesson_number=j, week=1, id_chat=id_chat) else Table.objects.filter(day=i, lesson_number=j, week=1, id_chat=id_chat)]
                dd[j] += [Table.objects.filter(day=i, lesson_number=j, week=0, id_chat=id_chat)[0] if Table.objects.filter(day=i, lesson_number=j, week=0, id_chat=id_chat) else Table.objects.filter(day=i, lesson_number=j, week=0, id_chat=id_chat)]

            data[i] = dd

    return data


def save_table(request) -> Dict:
    '''функция только для POST метода'''
    id_chat = request.POST['id_chat']

    data = {} # ключ - номер_урока.номер_дня.номер_недели.объект (1.1.1)
              # значение - список, 0 элемент - предмет, 1 - аудитория, 2 - преподаватель  
    for key in request.POST:

        try:
            # ключ-значение таблицы передается в виде
            # ключ - номер_урока.номер_дня.номер_недели.объект (объект : s - предмет, a - аудитория, t - преподаватель)
            # если элемент при сплите вызывает ошибку или количество элементов не равно 4, то также вызывается ошибка
            # и происходит переход к след элементу
            assert len(key.split('.')) == 4
        except:
            continue

        # key: str, делаем вырезку без последних двух элементов, 1.1.1.a -> 1.1.1 (точка тоже символ)
        data_key = key[:-2] # key_d - будущий ключ для словаря данных
        if data_key not in data:
            data[data_key] = [request.POST[key]]
        else:
            data[data_key] += [request.POST[key]]

    for key in data:
        if data[key]:
            try:
                wdl = key.split('.')
            except:
                continue

            record = Table.objects.get_or_create(id_chat=id_chat, lesson_number=wdl[0], day=wdl[1], week=wdl[2])[0]

            record.subject = data[key][0]
            record.auditorium = data[key][1]
            record.teacher = data[key][2]

            record.save()

    return get_data(request)


def index(request):

    content = {}

    if request.method == "POST":
        content['p'] = request.POST
        if 'save' in request.POST:
            content['post'] = request.POST
            try:
                data = save_table(request)
                content['data'] = data
            except:
                return render(request, 'index.html', content)

            content['id_editor'] = request.POST['id_editor']
            content['id_chat'] = request.POST['id_chat']


    if request.method == "GET":
        content['g'] = request.GET
        if 'id_editor' in request.GET and 'id_chat' in request.GET:
            content['get'] = request.GET
            try:
                data = get_data(request)
                content['data'] = data
            except:
                return render(request, 'index.html', content)

            content['id_editor'] = request.GET['id_editor']
            content['id_chat'] = request.GET['id_chat']
            

    return render(request, 'index.html', content)
