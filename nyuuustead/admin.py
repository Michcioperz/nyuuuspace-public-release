from django.contrib import admin

from nyuuustead.models import Userware, Hug, Pronoun, HugKind


@admin.register(Userware)
class UserwareAdmin(admin.ModelAdmin):
    list_display = 'user', 'colour', 'daily_notifications', 'hourly_notifications', 'news_emails'


@admin.register(Hug)
class HugAdmin(admin.ModelAdmin):
    list_display = 'source', 'kind', 'target'


@admin.register(Pronoun)
class PronounAdmin(admin.ModelAdmin):
    list_display = 'subject', 'object', 'possessive_determiner', 'possessive_pronoun', 'reflexive'


@admin.register(HugKind)
class HugKindAdmin(admin.ModelAdmin):
    list_display = 'name', 'past'