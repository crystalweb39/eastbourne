'''
@author: chaol
'''
import datetime
from django import forms
from django.forms.util import ErrorList
from captcha.fields import CaptchaField
class CommentForm(forms.Form):
    name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'class':'field-1'}))
    email = forms.EmailField(max_length=150, widget=forms.TextInput(attrs={'class':'field-1'}))
    comment = forms.CharField(max_length=600, widget=forms.Textarea(attrs={'class':'field-2'}))
    captcha = CaptchaField(error_messages={'invalid':'Invalid verification code. Please re-enter the code.'})
