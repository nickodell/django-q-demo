from django.db import models

# Create your models here.

class SumJob(models.Model):
    pass


class SumJobComponent(models.Model):
    # id = models.CharField(max_length=32, primary_key=True, editable=False)
    parent_job = models.ForeignKey(
        SumJob,
        on_delete=models.CASCADE,
    )
    result = models.BigIntegerField()
