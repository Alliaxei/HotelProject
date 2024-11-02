from tkinter.font import names

from django.contrib import admin
from django.urls import path

from hotelapp.views import login_page, admin_page, user_page, logout_view, add_user, delete_room, edit_client, \
    add_client, evict_client, add_room, edit_room, delete_user, edit_user, report_list, create_report, delete_report

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_page,name='login'),
    path('admin_page/', admin_page, name='admin_page'),
    path('user_page/', user_page, name='user_page'),
    path('logout/', logout_view, name='logout'),
    path('add_user/', add_user, name='add_user'),
    path('delete_room/<int:room_id>', delete_room, name='delete_room'),
    path('edit_client/', edit_client, name='edit_client'),
    path('add_client/', add_client, name='add_client'),
    path('evict_client/', evict_client, name='evict_client'),
    path('add_room/', add_room, name='add_room'),
    path('edit_room/', edit_room, name='edit_room'),
    path('delete_user/', delete_user, name='delete_user'),
    path('edit_user/', edit_user, name='edit_user'),
    path('reports/', report_list, name='reports'),
    path('reports/create', create_report, name='create_report'),
    path('delete_report', delete_report, name='delete_report'),

]
