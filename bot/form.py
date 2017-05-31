from django import forms
from .models import TeleUser,Word


class TeleUserForm(forms.ModelForm):
    class Meta:
        model=TeleUser
        fields = ['user_id','state']

class WordForm(forms.ModelForm):
    class Meta:
        model=Word
        fields=['teleuser','word']