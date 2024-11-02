from cProfile import label
from django import forms
from django.contrib.auth.password_validation import password_changed
from hotelapp.models import User, Client, Room, Report


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
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return self.instance.password
        return password

    # def clean_is_superuser(self):
    #     print("Вызов метода clean_is_superuser")
    #     is_superuser = self.cleaned_data.get('is_superuser')
    #     if isinstance(is_superuser, str):
    #         if is_superuser.lower() == 'true':
    #             return True
    #         elif is_superuser.lower() == 'false':
    #             return False
    #         return is_superuser


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

class ReportForm(forms.Form):
    class Meta:
        model = Report
        fields = '__all__'