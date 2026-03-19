from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import CustomUser


class VerificationCodeForm(forms.Form):
    verification_code = forms.CharField(label="Код подтверждения", max_length=6)

    class Meta:
        fields = "verification_code"

    def __init__(self, *args, **kwargs):
        super(VerificationCodeForm, self).__init__(*args, **kwargs)

        self.fields["verification_code"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите код подтверждения"}
        )

    def clean_verification_code(self):
        code = self.cleaned_data.get("verification_code")
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError("Код должен состоять из 6 цифр.")
        return code


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False)
    username = forms.CharField(max_length=50, required=True)
    usable_password = None

    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = CustomUser
        fields = ("email", "username", "first_name", "phone_number", "birth_date", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "type": "email", "placeholder": "Введите почту"}
        )

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Введите ник"})

        self.fields["first_name"].widget.attrs.update({"class": "form-control", "placeholder": "Введите ваше имя"})

        self.fields["phone_number"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите ваш номер",
            }
        )

        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Введите ваш пароль"})

        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Повторно введите ваш пароль"}
        )

        self.fields["birth_date"].widget.attrs.update(
            {"class": "form-control", "type": "date", "placeholder": "Введите дату рождения"}
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("номер телефона должен остоять только их цифр")
        return phone_number


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите почту"}),
    )
    password = forms.CharField(
        required=True, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Введите ваш пароль"})
    )

    class Meta:
        fields = ("username", "password")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["avatar", "email", "username", "phone_number", "gender", "pr_children"]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "type": "email", "placeholder": "Введите почту"}
        )

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Введите ник"})

        self.fields["phone_number"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите ваш номер",
            }
        )

        self.fields["pr_children"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Выберите наличие детей",
            }
        )

        self.fields["gender"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Выберите ваш пол",
            }
        )


class ResetPasswordForm(forms.Form):

    class Meta:
        model = CustomUser
        fields = ["email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Введите почту"})

        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Введите новый пароль"})

        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Повторно введите новый пароль"}
        )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={"class": "form-input"}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={"class": "form-input"}))
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
