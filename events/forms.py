from django import forms

from .models import Event


class EventForm(forms.ModelForm):

    class Meta:
        model = Event

        fields = [
            "name",
            "poster",
            "description",
            "min_age",
            "date_start",
            "is_archive",
            "recommend_audit_gender",
            "recommend_audit_age",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "date_start": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"
            ),
            "recommend_audit_age": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):

        kwargs.pop("user", None)
        super(EventForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.widget.attrs.get("class"):
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs.update({"class": "form-control"})

        self.fields["name"].widget.attrs.update({"placeholder": "Введите название мероприятия"})
        self.fields["description"].widget.attrs.update({"placeholder": "Красочное описание события..."})
        self.fields["min_age"].widget.attrs.update({"placeholder": "Например: 18"})

        self.fields["date_start"].widget.attrs.update({"placeholder": "Выберите дату и время"})

        self.fields["is_archive"].widget.attrs.update({"class": "form-check-input"})
