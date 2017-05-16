from django.db import models

class TeleUser (models.Model):
    first_name=models.CharField(max_length=10000)
    last_name=models.CharField(max_length=10000, blank=True)
    user_name=models.CharField(max_length=1111121)
    user_id=models.IntegerField()
    state=models.IntegerField()


class Word(models.Model):
    teleuser=models.ForeignKey(TeleUser)
    word=models.CharField(max_length=1231312312312312313)
    meaning=models.CharField(max_length=1231312312312312313, null=True)
    # photo=models.CharField(max_length=1231312312312312313)
    # last_review=models.TimeField(null=True)
    last_review_status=models.BooleanField(default=False)
    next_review_time=models.TimeField(null=True)
    level=models.IntegerField(default=0)