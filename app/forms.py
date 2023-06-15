from django import forms
from .models import Survey

class SurveyForm(forms.ModelForm):
    age = forms.IntegerField(required=True)
    gender = forms.ChoiceField(choices=(("male", "male"), ("female", "female")), required=True)
    years_in_crypto = forms.IntegerField(required= True)
    own_nfts = forms.ChoiceField(choices=(("yes", "yes"), ("no", "no")),required= True)
    own_cryptos = forms.ChoiceField(choices=(("yes", "yes"), ("no", "no")), required=True)
    money_invested = forms.FloatField(required= True)

    class Meta:
        model = Survey
        fields = ('age', 'gender','years_in_crypto', 'own_nfts', 'own_cryptos','money_invested')

