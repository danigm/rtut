from django.db import models
from django.contrib.auth.models import User


class HourAvaliable(models.Model):
    user = models.ForeignKey(User)
    hour = models.DateTimeField()
    time = models.FloatField()

    def booker(self):
        if self.booking_set.count():
            b = self.booking_set.all()[0]
            return '%s, %s' % (b.user_name, b.comment)
        else:
            return ''

    class Meta:
        ordering = ['hour']

    def __unicode__(self):
        return "%s: %s - %s" % (self.user.username, self.hour.ctime(), self.time)


class Booking(models.Model):
    hour_avaliable = models.ForeignKey(HourAvaliable, unique=True)
    user_name = models.CharField(max_length=255)
    email = models.EmailField()
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.user_name, self.hour_avaliable)
