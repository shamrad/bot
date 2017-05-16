from django import forms
from .models import TeleUser,Word


class TeleUserForm(forms.ModelForm):
    class Meta:
        model=TeleUser
        fields = ['first_name',  'user_name', 'user_id','state']

class WordForm(forms.ModelForm):
    class Meta:
        model=Word
        fields=['teleuser','word']