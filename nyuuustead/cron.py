from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django_cron import CronJobBase, Schedule


class CronDailyNotifications(CronJobBase):
    schedule = Schedule(run_at_times=['13:37'])
    code = 'nyuuustead.dailynotifications'

    def do(self):
        for u in User.objects.select_related("userware").filter(userware__daily_notifications=True).all():
            notifiable = list(u.userware.hugs_to_notify.order_by('-timestamp').all())[:10]
            u.userware.hugs_to_notify.clear()
            if len(notifiable) > 0:
                context = dict(hugs=notifiable, user=u)
                u.email_user(subject="Daily notifications up from the nyuuuspace",
                             message=render_to_string('notifications.txt', context),
                             html_message=render_to_string('notifications.html', context))


class CronHourlyNotifications(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = 'nyuuustead.hourlynotifications'

    def do(self):
        for u in User.objects.select_related("userware").filter(userware__hourly_notifications=True).all():
            notifiable = list(u.userware.hugs_to_notify.order_by('-timestamp').all())[:10]
            u.userware.hugs_to_notify.clear()
            if len(notifiable) > 0:
                context = dict(hugs=notifiable, user=u)
                u.email_user(subject="Hourly notifications up from the nyuuuspace",
                             message=render_to_string('notifications.txt', context),
                             html_message=render_to_string('notifications.html', context))
