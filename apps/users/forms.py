from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    nickname = forms.CharField(max_length=50, label='Nickname', 
                               widget=forms.TextInput(attrs={'placeholder': 'Gaming lakabingizni yozing'}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.nickname = self.cleaned_data['nickname']
        user.save()
        return user