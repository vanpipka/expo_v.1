from django.forms import ModelForm
from django import forms
from .models import Comments

class CommentForm(ModelForm):
    """Форма комментариев к статьям
    """
    class Meta:
        model = Comments
        fields = ('text', 'rating', 'idProf')