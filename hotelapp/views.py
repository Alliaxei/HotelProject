from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404  # redirect делает переход на необходимую страницу
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import UserForm, ClientForm, RoomForm
from .models import Room, User, Client


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser == 1:
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
            #user.password = form.cleaned_data['password']
            user.save()
            return JsonResponse({"message": "Пользователь успешно создан"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse({"error": "Неверный запрос"}, status=400)

@login_required
def add_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_page')
        else:
            print("Form errors:", form.errors)
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
        pass

@login_required
def admin_page(request):
    rooms = Room.objects.all()
    users = User.objects.all()
    context = {'rooms': rooms,
               'users': users}
    return render(request, 'adminPageHotel.html', context)

@login_required
def user_page(request):
    user_id = request.user.id

    clients = Client.objects.all()
    rooms = Room.objects.all()

    context = {#'user_id': user_id,
               'clients': clients,
               'rooms': rooms}
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

@login_required
def add_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('user_page')
    else:
        form = ClientForm()
    return render(request, 'add_client.html', {'form': form})

@require_POST
def evict_client(request):
    client_id = request.POST.get('client_id')
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return redirect('user_page')
