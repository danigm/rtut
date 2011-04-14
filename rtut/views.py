import re
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rtut.models import Booking, HourAvaliable

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.conf import settings


def cal(request, username):
    user = get_object_or_404(User, username=username)
    today = datetime.datetime.now()
    while today.weekday() != 0:
        today = today - datetime.timedelta(1)

    days = []
    for i in range(4):
        week = []
        for j in range(7):
            day = today + datetime.timedelta(7*i + j)
            query = user.houravaliable_set.filter(hour__day=day.day, hour__month=day.month)
            n = query.count()
            m = Booking.objects.filter(hour_avaliable__in=query).count()
            week.append((day, query, n, m))
        days.append(week)

    return render_to_response('rtut/cal.html', {'today': today,
                                                'user': request.user,
                                                'username': username,
                                                'show_booker': settings.SHOW_BOOKER,
                                                'days': days},
                              context_instance=RequestContext(request))


def day(request, username, day, month, year):
    user = get_object_or_404(User, username=username)
    hour_avaliable = user.houravaliable_set.filter(hour__day=day, hour__month=month)
    booking = Booking.objects.filter(hour_avaliable__in=hour_avaliable)

    return render_to_response("rtut/day.html", {'user': user,
                                                'hour_avaliable': hour_avaliable,
                                                'booking': booking,
                                                'day':
                                                datetime.datetime(int(year),
                                                int(month),
                                                int(day))},
                              context_instance=RequestContext(request))


class BookingForm(ModelForm):
    class Meta:
        model = Booking
        exclude = ("hour_avaliable", )


def booking(request, username, day, month, year, ha_id):
    ha = get_object_or_404(HourAvaliable, pk=ha_id)
    booked = ha.booking_set.all().count()
    if not booked and request.method == "POST":
        if request.POST['subject']:
            return HttpResponse("no spam please")
        form = BookingForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.hour_avaliable = ha
            b.save()
            send_mail(_('Booking done [%s]' % ha.hour.ctime()),
                      _('Booking done by %(user)s (%(email)s) '
                        'for %(time)s\n\nComment:\n%(comment)s' %\
                        {'user': b.user_name,
                         'email': b.email,
                         'time': ha.hour.ctime(),
                         'comment': b.comment}),
                      settings.DEFAULT_FROM_EMAIL,
                      [ha.user.email, b.email], fail_silently=True)
            return redirect("rtut.views.cal", username)
    else:
        form = BookingForm()

    day = ha.hour

    return render_to_response("rtut/booking.html", {'booked': booked,
                                                    'form': form,
                                                    'day': day},
                              context_instance=RequestContext(request))


class DefForm(forms.Form):
    d = datetime.datetime.now()
    dates = forms.CharField(label=_("Dates"),
                initial=d.strftime("%d/%m/%y-%d/%m/%y"),
                help_text=_("format: 'dd/mm/yy-dd/mm/yy'"))
    hours = forms.CharField(label=_("Hours"),
                initial=d.strftime("%H:%M-%H:%M"),
                help_text=_("format: 'hh:mm-hh:mm'"))
    all = forms.BooleanField(required=False, label=_("all"), initial=True)
    mon = forms.BooleanField(required=False, label=_("mon"))
    tue = forms.BooleanField(required=False, label=_("tue"))
    wed = forms.BooleanField(required=False, label=_("wed"))
    thu = forms.BooleanField(required=False, label=_("thu"))
    fri = forms.BooleanField(required=False, label=_("fri"))
    sat = forms.BooleanField(required=False, label=_("sat"))
    sun = forms.BooleanField(required=False, label=_("sun"))

    def clean_dates(self):
        data = self.cleaned_data['dates']
        date1, date2 = None, None
        fmt = '%d/%m/%y'
        try:
            date1, date2 = data.split('-')
            date1 = datetime.datetime.strptime(date1, fmt)
            date2 = datetime.datetime.strptime(date2, fmt)
        except:
            raise forms.ValidationError(_("Wrong format, use 'dd/mm/yy-dd/mm/yy'"))

        return date1, date2

    def clean_hours(self):
        data = self.cleaned_data['hours']
        hour1, hour2 = None, None
        fmt = '%H:%M'
        try:
            hour1, hour2 = data.split('-')
            hour1 = datetime.datetime.strptime(hour1, fmt)
            hour2 = datetime.datetime.strptime(hour2, fmt)
        except:
            raise forms.ValidationError(_("Wrong format, use 'hh:mm-hh:mm'"))

        return hour1, hour2


@login_required
def defcal(request):
    user = request.user
    if request.method == 'POST':
        f = DefForm(request.POST)
        if f.is_valid():
            data = f.cleaned_data
            date1, date2 = data['dates']
            hour1, hour2 = data['hours']
            if data['all']:
                weekdays = [True] * 7
            else:
                weekdays = [data['mon'], data['tue'],
                            data['wed'], data['thu'],
                            data['fri'], data['sat'],
                            data['sun']]
            d = date1
            while d <= date2:
                if not weekdays[d.weekday()]:
                    d = d + datetime.timedelta(1)
                    continue
                h = hour1
                while h < hour2:
                    rd = datetime.datetime(d.year, d.month, d.day, h.hour, h.minute)
                    ha = HourAvaliable(user=user, hour=rd, time=settings.TIME_SLICE)
                    ha.save()
                    h = h + datetime.timedelta((1 / 24.) * settings.TIME_SLICE)
                d = d + datetime.timedelta(1)

            return redirect(cal, user.username)

    else:
        f = DefForm()
    return render_to_response("rtut/def.html",
                              {'form': f},
                              context_instance=RequestContext(request))


def all(request):
    allusers = User.objects.all()
    return render_to_response('rtut/all.html', {'allusers': allusers},
                              context_instance=RequestContext(request))

