from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from config.settings import DEFAULT_FROM_EMAIL


class ContactsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "restaurants/contacts.html"
    success_url = reverse_lazy("restaurants:contacts")

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        message = request.POST.get("message")
        email = request.POST.get("email")

        subject = "Поддержка"
        message = f'Сообщение:"{message}". Электронная почта для связи: {email}({name}).'
        from_email = DEFAULT_FROM_EMAIL
        recipient_list = [
            DEFAULT_FROM_EMAIL,
        ]
        send_mail(subject, message, from_email, recipient_list)

        return redirect(self.success_url)
