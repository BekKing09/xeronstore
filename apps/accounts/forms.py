from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileEditForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ['nickname', 'avatar']
        widgets = {
            'nickname': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nicknamesiz'
            }),
        }