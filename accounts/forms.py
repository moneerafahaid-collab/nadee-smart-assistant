from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class EmployeeLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(
            attrs={
                "class": "field-input",
                "placeholder": "أدخل اسم المستخدم",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(
            attrs={
                "class": "field-input",
                "placeholder": "أدخل كلمة المرور",
                "autocomplete": "current-password",
            }
        ),
    )


class EmployeeRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="الاسم الأول", max_length=150)
    last_name = forms.CharField(label="اسم العائلة", max_length=150)
    email = forms.EmailField(label="البريد الإلكتروني")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "اسم المستخدم"
        self.fields["password1"].label = "كلمة المرور"
        self.fields["password2"].label = "تأكيد كلمة المرور"
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "field-input")
