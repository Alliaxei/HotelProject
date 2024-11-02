from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404  # redirect делает переход на необходимую страницу
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import UserForm, ClientForm, RoomForm, ReportForm
from .models import Room, User, Client, Invoice, Report

client_count = 0
room_used_count = 0

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_admin == 1:
                return redirect('admin_page')
            else:
                return redirect('user_page')
        else:
            context = {'error': 'Неверный логин или пароль'}
            return render(request, 'loginPagehotel.html', context)
    return render(request, 'loginPagehotel.html')

@csrf_exempt
@login_required
def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            #commit=False - не сохраняет пользователя в БД
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_superuser = form.cleaned_data.get('is_superuser', False)
            #user.password = form.cleaned_data['password']
            user.save()
            return redirect('admin_page')
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse({"error": "Неверный запрос"}, status=400)

def edit_user(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)  # Получаем пользователя по id

        form = UserForm(request.POST, instance=user)  # Передаем instance пользователя в форму

        if form.is_valid():
            form.save()  # Сохраняем изменения через форму (включая валидацию)
            return redirect('admin_page')  # После успешного сохранения перенаправляем на админскую страницу
        else:

            return JsonResponse({"error": form.errors}, status=400)  # Отправляем ошибки валидации

    return JsonResponse({"error": "Неверный запрос"}, status=400)

def delete_user(request):
    user_id = request.POST.get('user_id')
    user = get_object_or_404(User,id=user_id)
    user.delete()
    return redirect('admin_page')

@login_required
def add_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        room_number = request.POST.get('room_number')

        # Проверка на существование номера комнаты
        if Room.objects.filter(room_number=room_number).exists():
            messages.error(request, f'Номер {room_number} уже существует.')
        elif form.is_valid():
            form.save()
            return redirect('admin_page')
        else:
            # Если форма невалидна, ошибки будут обработаны здесь
            messages.error(request, 'Произошла ошибка при добавлении комнаты. Проверьте введенные данные.')

        rooms = Room.objects.all()
        users = User.objects.all()
        return render(request, "adminPageHotel.html", {'form': form, 'rooms': rooms, 'users': users})

    else:
        form = RoomForm()
        rooms = Room.objects.all()
        users = User.objects.all()
        return render(request, "adminPageHotel.html", {'form': form, 'rooms': rooms, 'users': users})

@login_required
def edit_room(request):
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        if not room_id:
            return JsonResponse({"error" : "room_id не указан"}, status=400)

        room = get_object_or_404(Room,id=room_id)
        room.room_number = request.POST.get('room_number')
        room.building = request.POST.get('building')
        room.floor = request.POST.get('floor')
        room.room_category = request.POST.get('room_category')
        room.bathRoomType = request.POST.get('bathRoomType')
        room.numberOfSeats = request.POST.get('numberOfSeats')
        room.save()
        return redirect('admin_page')
    return JsonResponse({"error": "Неверный запрос"}, status=400)

@login_required
def admin_page(request):
    rooms = Room.objects.all()
    users = User.objects.filter(is_admin=False)
    reports = Report.objects.all()
    context = {'rooms': rooms,
               'users': users,
               'reports': reports}
    return render(request, 'adminPageHotel.html', context)

@login_required
def user_page(request):
    user_id = request.user.id
    reports = Report.objects.all()

    is_superuser = request.user.is_superuser
    clients = Client.objects.all()
    rooms = Room.objects.all()

    context = {#'user_id': user_id,
               'clients': clients,
               'rooms': rooms,
               'is_superuser': is_superuser,
               'reports': reports,
    }
    return render(request, 'userPageHotel.html', context)

def logout_view(request):
    request.session.flush()
    return redirect('login')

def delete_room(request, room_id):
    room = get_object_or_404(Room,id=room_id)
    room.delete()
    return redirect('admin_page')

@login_required
def edit_client(request):
    if request.method == "POST":
        client_id = request.POST.get('client_id')
        if not client_id:
            return JsonResponse({"error" : "client_id не указан"}, status=400)

        client = get_object_or_404(Client, id=client_id)
        client.name = request.POST.get('name')
        client.passport = request.POST.get('passport')
        room_id = request.POST.get('room')
        if not room_id:
            return JsonResponse({"error": "room_id не указан"}, status=400)

        client.room = get_object_or_404(Room, id=room_id)
        client.lengthOfStay = request.POST.get('lengthOfStay')
        client.save()
        return redirect('user_page')
    return JsonResponse({"error": "Неверный запрос"}, status=400)

# @login_required
# def add_client(request):
#     if request.method == "POST":
#         form = ClientForm(request.POST)
#
#         if form.is_valid():
#             form.save()
#             return redirect('user_page')
#     else:
#         form = ClientForm()
#     return render(request, 'add_client.html', {'form': form})

def add_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)

        if form.is_valid():
            client = form.save()

            # После добавления клиента меняем статус комнаты на занятую
            room = client.room
            room.is_occupied = True
            room.save()

            return redirect('user_page')
    else:
        form = ClientForm()

    return render(request, 'add_client.html', {'form': form})

@require_POST
# def evict_client(request):
#     if request.method == "POST":
#         client_id = request.POST.get('client_id')
#         client = get_object_or_404(Client, id=client_id)
#
#         days_billed = client.lengthOfStay
#         daily_rate = 10
#         total_amount = days_billed * daily_rate
#
#         Invoice.objects.create(client=client_id, amount=total_amount)
#
#         client.delete()
#         return redirect('user_page')


def evict_client(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        client = get_object_or_404(Client, id=client_id)

        days_billed = client.lengthOfStay
        daily_rate = 10
        total_amount = days_billed * daily_rate

        Invoice.objects.create(client=client, amount=total_amount)
        room = client.room

        client.delete()

        if not Client.objects.filter(room=room).exists():
            room.is_occupied = False
        else:
            room.is_occupied = True

        room.save()
        return redirect('user_page')


# def get_evict_info(request, client_id):
#     client = get_object_or_404(Client, id=client_id)
#
#     days_billed = client.lengthOfStay
#     daily_rate = 10
#     total_amount = days_billed * daily_rate
#
#     return render(request, 'your_template.html', {
#         'client': client,
#         'invoice_info': f'Счёт: {client.id}, Клиент: {client.name}, Сумма: {total_amount} рублей'
#     })

def report_list(request):
    reports = Report.objects.all()

    return render('')

def create_report(request):
    if request.method == 'POST':
        client_count = Client.objects.count()
        room_used_count = Room.objects.filter(is_occupied=True).count()
        preferencies = request.POST.get('preferencies')
        report = Report(count_of_clients=client_count, count_of_rooms=room_used_count, preferencies=preferencies)

        report.save()
        print(preferencies)
        print(f'Комнаты: {room_used_count}')
        print(f'Клиенты: {client_count}')

        return redirect('user_page')

def delete_report(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        report = get_object_or_404(Report, id=report_id)
        report.delete()
        return redirect('admin_page')
