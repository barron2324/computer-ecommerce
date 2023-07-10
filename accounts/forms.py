from django import forms
from .models import Account, Userprofile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'รหัสผ่าน',
        'class': 'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'ยืนยันรหัสผ่าน',
        'class': 'form-control'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'ชื่อ'
        self.fields['last_name'].widget.attrs['placeholder'] = 'สกุล'
        self.fields['email'].widget.attrs['placeholder'] = 'อีเมลล์'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'เบอร์โทร'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "รหัสผ่านของคุณไม่ตรงกัน ลองอีกครั้ง"
            )
        
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("ไฟล์ภาพเท่านั้น")}, widget=forms.FileInput)
    class Meta:
        model = Userprofile
        fields = ('address_line_1', 'address_line_2', 'district', 'province', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'