from django import forms
from .models import CreateAuthor, CreateQuote, Author


class CreateAuthorForm(forms.ModelForm):
    class Meta:
        model = CreateAuthor
        fields = ["name", "born_date", "born_location", "description"]


class CreateQuoteForm(forms.ModelForm):
    author = forms.CharField(max_length=100, label="Author")
    tags = forms.CharField(required=False, label="Tags")

    class Meta:
        model = CreateQuote
        fields = ["quote", "author", "tags"]

    def clean_author(self):
        name = self.cleaned_data['author'].strip()
        try:
            return Author.objects.get(name=name)  # noqa
        except Author.DoesNotExist:  # noqa
            raise forms.ValidationError("Author does not exist. Please create it first.")
