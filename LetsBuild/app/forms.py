
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth.models import User

from django import forms

from django.forms.widgets import PasswordInput, TextInput

class CreateUserForm(UserCreationForm): #user creation

    class Meta:

        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.fields.values():
            f.widget.attrs.update({
                "class": "form-control form-control-lg",
                "placeholder": f.label,
            })

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget= TextInput())
    password = forms.CharField(widget= PasswordInput())

