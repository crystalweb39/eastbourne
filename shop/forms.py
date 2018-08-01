'''
@author: chaol
'''
import datetime
from django import forms
from django.forms.util import ErrorList
from eastbourne.userprofile.models import Country

from eastbourne.shop import generateAmountHash

from django.contrib.auth.models import User

from django.contrib.auth import authenticate as _authenticate
from django.contrib.auth import login as _login
from django.contrib.auth import logout as _logout

class CustomerDetailsForm(forms.Form):
    billfirstname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    billlastname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    billcompany = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billaddress = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    billaddress2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billaddress3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billsuburb = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    billstate = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    billpostcode = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class':'field-1'}))
    billcountry = forms.ModelChoiceField(queryset=Country.objects.filter(shipto=True).order_by("country"), empty_label="Select your Country...", widget=forms.Select(attrs={'class':'field-1'}))
    billphone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billemail = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipfirstname = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shiplastname = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipcompany = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipaddress = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipaddress2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipaddress3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipsuburb = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipstate = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shippostcode = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class':'field-3','disabled':'disabled'}))
    shipcountry = forms.ModelChoiceField(queryset=Country.objects.filter(shipto=True).order_by('country'), empty_label="Select your Country...", widget=forms.Select(attrs={'class':'field-3','disabled':'disabled'}))
    shipphone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    subscribe = forms.TypedChoiceField(required=True, coerce=bool, choices=[[1, "Yes please"], [0, "No thank you"]], widget=forms.RadioSelect(attrs={'class':'field-1'}))
    copydata = forms.BooleanField(required=False)
    agree = forms.BooleanField(required=True)
    
    
class CustomerWDetailsForm(forms.Form):
    billfirstname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    billlastname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    billcompany = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billaddress = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    billaddress2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billaddress3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billsuburb = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    billstate = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    billpostcode = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class':'field-1'}))
    billcountry = forms.ModelChoiceField(queryset=Country.objects.filter(shipto=True).order_by("country"), empty_label="Select your Country...", widget=forms.Select(attrs={'class':'field-1'}))
    billphone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    billemail = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipfirstname = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shiplastname = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipcompany = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipaddress = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipaddress2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipaddress3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipsuburb = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shipstate = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    shippostcode = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class':'field-1'}))
    shipcountry = forms.ModelChoiceField(queryset=Country.objects.filter(shipto=True).order_by('country'), empty_label="Select your Country...", widget=forms.Select(attrs={'class':'field-1'}))
    shipphone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    subscribe = forms.TypedChoiceField(required=True, coerce=bool, choices=[[1, "Yes please"], [0, "No thank you"]], widget=forms.RadioSelect(attrs={'class':'field-1'}))
    copydata = forms.BooleanField(required=False)
    agree = forms.BooleanField(required=True)
class WholesaleLoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class':'field-1'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'field-1'}))
    user = None
    def clean(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        username = email
        username = username.replace("@", "_")
        username = username.replace(".", "_")
        password = self.cleaned_data.get("password","")
        self.user = _authenticate(username=username, password=password)
        if self.user:
            if self.user.is_active:
                return self.cleaned_data
            else:
                raise forms.ValidationError("Your account is pending approval.")
        else:
            raise forms.ValidationError("Login Failed")
class WholesaleProfilePrimaryContactForm(forms.Form):
    firstname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    lastname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    phone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    fax = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    company = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    tradingas = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    abn = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    subscribe = forms.TypedChoiceField(required=True, choices=[[1, "Yes please"], [0, "No thank you"]], widget=forms.RadioSelect(attrs={'class':'field-1'}))
class WholesaleProfileEmailForm(forms.Form):
    current = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    email2 = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    def clean_email(self):
        try:
            username = self.cleaned_data['email'].strip().lower()
            username = username.replace("@", "_")
            username = username.replace(".", "_")
            User.objects.get(username=username)
        except Exception, e:
            return self.cleaned_data['email']
        raise forms.ValidationError("This email address is already registered")
class WholesaleProfilePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'field-1'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'field-1'}))
    def clean_email2(self):
        if self.cleaned_data.has_key("email"):
            if self.cleaned_data['email2'] == self.cleaned_data['email']:
                return self.cleaned_data['email2']
            else:
                raise forms.ValidationError("Email Addresses don't match")
        else:
            return ""
    def clean_password2(self):
        if self.cleaned_data['password2'] == self.cleaned_data['password']:
            return self.cleaned_data['password2']
        else:
            raise forms.ValidationError("Passwords don't match")
class WholesaleProfileAddressForm(forms.Form):
    address = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    address3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    suburb = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    postcode = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class':'field-1'}))
    country = forms.ModelChoiceField(queryset=Country.objects.filter(shipto=True), empty_label="Select your Country...", widget=forms.Select(attrs={'class':'field-1'}))
    
    def clean_email(self):
        try:
            username = self.cleaned_data['email'].strip().lower()
            username = username.replace("@", "_")
            username = username.replace(".", "_")
            User.objects.get(username=username)
        except Exception, e:
            return self.cleaned_data['email']
        raise forms.ValidationError("This email address is already registered")
    def clean_email2(self):
        if self.cleaned_data.has_key("email"):
            if self.cleaned_data['email2'] == self.cleaned_data['email']:
                return self.cleaned_data['email2']
            else:
                raise forms.ValidationError("Email Addresses don't match")
        else:
            return ""
    def clean_password2(self):
        if self.cleaned_data['password2'] == self.cleaned_data['password']:
            return self.cleaned_data['password2']
        else:
            raise forms.ValidationError("Passwords don't match")

class WholesaleForm(forms.Form):
    firstname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    lastname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    email2 = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    phone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    fax = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    company = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    tradingas = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    abn = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    address3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'field-1'}))
    suburb = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class':'field-1'}))
    postcode = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class':'field-1'}))
    country = forms.ModelChoiceField(queryset=Country.objects.filter(shipto=True).order_by("country"), empty_label="Select your Country...", widget=forms.Select(attrs={'class':'field-1'}))
    subscribe = forms.TypedChoiceField(required=True, coerce=str, choices=[["1", "Yes please"], ["0", "No thank you"]], widget=forms.RadioSelect(attrs={'class':'field-1'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'field-1'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'field-1'}))
    def clean_email(self):
        try:
            username = self.cleaned_data['email'].strip().lower()
            username = username.replace("@", "_")
            username = username.replace(".", "_")
            User.objects.get(username=username)
        except Exception, e:
            return self.cleaned_data['email']
        raise forms.ValidationError("This email address is already registered")
    def clean_email2(self):
        if self.cleaned_data.has_key("email"):
            if self.cleaned_data['email2'] == self.cleaned_data['email']:
                return self.cleaned_data['email2']
            else:
                raise forms.ValidationError("Email Addresses don't match")
        else:
            return ""
    def clean_password2(self):
        if self.cleaned_data['password2'] == self.cleaned_data['password']:
            return self.cleaned_data['password2']
        else:
            raise forms.ValidationError("Passwords don't match")
class WholesaleForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'field-1'}))
    def clean_email(self):
        try:
            return self.cleaned_data['email']
        except Exception, e:
            raise forms.ValidationError("We were unable to find this email address.")
def generateMonths():
    return [[str(x).zfill(2),str(x).zfill(2)] for x in range(1, 13)]
def generateYears():
    d = datetime.datetime.now()
    return [[str(x),str(x)] for x in range(d.year, d.year+11)]
class CreditCardForm(forms.Form):
    name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'class':'field-1'}))
    type = forms.CharField(max_length=10, widget=forms.Select(attrs={'class':'field-1'}, choices=(("VISA", "VISA",), ("Mastercard", "Mastercard",))))
    number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'field-1'}))
    expiryMonth = forms.IntegerField(widget=forms.Select(attrs={'class':'expiryfield'}, choices=generateMonths()))
    expiryYear = forms.IntegerField(widget=forms.Select(attrs={'class':'expiryfield'}, choices=generateYears()))
    CVV = forms.CharField(widget=forms.TextInput(attrs={'maxlength': 4, 'size': 4, 'class':'smallfield-1'}))
    amount = forms.FloatField(widget=forms.HiddenInput())
    hash = forms.CharField(widget=forms.HiddenInput())
    errormessage = ""
    #
    # Next 2 methods are validation of the credit card number.
    #
    
    def clean_name(self):
        temp = self.cleaned_data['name'].strip().split(' ')
        if len(temp) != 2:
            raise forms.ValidationError("Please insert name as this: Firstname Lastname")
        else:
            return self.cleaned_data['name']
    def clean_hash(self):
        if self.cleaned_data['hash'] == generateAmountHash(self.cleaned_data['amount']):
            return self.cleaned_data['hash']
        else:
            raise forms.ValidationError("Amount checksum mismatch")
    def check_number(self, number):
        """
        Luhn credit card number check
        """
        number = number.replace(" ", "")
        number = number.replace("-", "")
        try:
            number = int(number)
        except:
            return False
        digits = number
        _sum = 0
        alt = False
        ix = []
        for x in str(digits):
            ix.append(int(x))
        for d in reversed(ix):
            assert 0 <= d <= 9
            if alt:
                d *= 2
                if d > 9:
                    d -= 9
            _sum += d
            alt = not alt
        return (_sum % 10) == 0
    def processingError(self, msg):
        self.errormessage = msg
    def clean(self):
        return self.cleaned_data
    # do the forms validation for the ccnumber
    def clean_number(self):
        if self.check_number(self.cleaned_data['number']):
            return self.cleaned_data['number']
        else:
            raise forms.ValidationError("Number failed verification")
    # check to make sure their credit card hasn't expired
    def clean_expiryYear(self):
        now = datetime.datetime.now()
	day = now.day if now.day <= 28 else 28
        exp = datetime.datetime(self.cleaned_data['expiryYear'], self.cleaned_data['expiryMonth'], day)
        if now <= exp or (now.month == exp.month and now.year == exp.year):
            return self.cleaned_data['expiryYear']
        else:
            raise forms.ValidationError("Your card has expired")
