from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
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
    email = forms.EmailField(
        label="Электронная почта",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "your_email@example.com"}),
    )
    username = forms.CharField(
        label="Имя пользователя",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Например: Сибиряк_88"}),
    )
    first_name = forms.CharField(
        label="Ваше имя",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите ваше имя"}),
    )
    phone_number = forms.CharField(
        label="Номер телефона",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7 (XXX) XXX-XX-XX"}),
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "placeholder": "ДД.ММ.ГГГГ"}),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username", "first_name", "phone_number", "birth_date", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if "form-control" not in field.widget.attrs.get("class", "").split():
                current_classes = field.widget.attrs.get("class", "").split()
                current_classes.append("form-control")
                field.widget.attrs["class"] = " ".join(current_classes)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


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
        fields = ["avatar", "email", "username", "phone_number", "gender", "birth_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if "form-control" not in field.widget.attrs.get("class", "").split():
                current_classes = field.widget.attrs.get("class", "").split()
                current_classes.append("form-control")
                field.widget.attrs["class"] = " ".join(current_classes)

        if self.instance and getattr(self.instance, "pk", None):
            existing_bd = getattr(self.instance, "birth_date", None)
            if existing_bd:
                self.fields["birth_date"].disabled = True
                self.fields["birth_date"].widget.attrs["readonly"] = True
                self.fields["birth_date"].help_text = "Дата рождения уже указана и не может быть изменена."


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


class BerlogaPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "example@mail.com"})
