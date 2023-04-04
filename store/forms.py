from django import forms
from .models import Customer, Product


class ProductForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=7,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Product
        fields = ('name', 'price', 'image', 'collection')
        exclude = ('digital',)

class SignupForm(forms.ModelForm):
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ['store_name', 'whatsapp_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match')

        return confirm_password
    

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)