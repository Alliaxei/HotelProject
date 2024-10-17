from cProfile import label

from django import forms

from hotelapp.models import User, Client, Room


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=255)
    password = forms.CharField


class UserForm(forms.ModelForm):
    class Meta:
        #Указывает форме, что она должна использовать поля из модели User
        model = User
        #Указывает какие поля будут включены в форму
        fields = ['login',
                  'password',
                   'is_superuser']
        #Виджет определяет, как поле будет отображаться в html
        widgets = {
            # forms.PasswordInput() означает, что будет использоваться элемент input type="password"
            'password': forms.PasswordInput()
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'