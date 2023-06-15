from djongo import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Survey(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'user')
    datetime = models.DateTimeField(blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length= 6, choices=(("male", "male"), ("female", "female")))
    years_in_crypto = models.IntegerField()
    own_nfts = models.CharField(max_length= 3, choices=(("yes", "yes"), ("no", "no")))
    own_cryptos = models.CharField(max_length= 3, choices=(("yes", "yes"), ("no", "no")))
    money_invested = models.FloatField()

    def save(self, *args, **kwargs):
        super(Survey, self).save(*args, **kwargs)