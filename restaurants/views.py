from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView

from config.settings import DEFAULT_FROM_EMAIL
from restaurants.models import TeamMember


class ContactsTemplateView(LoginRequiredMixin, TemplateView):
    """Представление страницы с контактной информацией"""

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


class AboutUsView(TemplateView):
    """Представление странииы 'О нас'"""

    template_name = "restaurants/about_us.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["bosses"] = TeamMember.objects.filter(position_department="Начальство", is_public=True)
        context["team_kitchen"] = TeamMember.objects.filter(position_department="Кухня", is_public=True)
        context["team_hall"] = TeamMember.objects.filter(position_department="Зал", is_public=True)

        return context


class ShowMenuView(TemplateView):
    """Представление странииы 'Меню'"""

    template_name = "restaurants/menu.html"
