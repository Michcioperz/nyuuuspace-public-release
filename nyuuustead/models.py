import random, json

from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django_redis import get_redis_connection

BEST_COLOURS = (
    "#1b85b8",
    "#03c03c",
    "#559e83",
    "#ae5a41",
    "#c3cb71",
    "#c23b22",
    "#ffb347",
    "#f49ac2",
    "#dea5a4",
    "#e3e387",
    "#77dd77",
    "#b19cd9",
    "#ffd1dc",
    "#779ecb",
    "#cb99c9",
    "#966fd6"
)


def best_colour():
    return random.choice(BEST_COLOURS)


def best_hug():
    return HugKind.objects.order_by('?')[0]


class Pronoun(models.Model):
    subject = models.CharField(max_length=20)
    object = models.CharField(max_length=20)
    possessive_determiner = models.CharField(max_length=20)
    possessive_pronoun = models.CharField(max_length=20)
    reflexive = models.CharField(max_length=25)

    def __str__(self):
        return "/".join(
            (self.subject, self.object, self.possessive_determiner, self.possessive_pronoun, self.reflexive))


class Userware(models.Model):
    user = models.OneToOneField(User, related_name="userware")
    daily_notifications = models.BooleanField(default=True, help_text="Those will be sent to your email no more often" +
                                              " than once a day, at 13:37 server time.")
    hourly_notifications = models.BooleanField(default=False, help_text="Those will be sent to your email no more oft" +
                                               "en than once per hour.")
    news_emails = models.BooleanField(default=True, help_text="Those will be sent whenever I have something to announ" +
                                      "ce, which probably won't be too often.")
    colour = RGBColorField(default=best_colour, colors=BEST_COLOURS)
    pronoun = models.ForeignKey(Pronoun, related_name="pronouns",
                                help_text="Is your pronoun missing? Shoot an email " +
                                          "at michcioperz@gmail.com and we'll look into it!")
    followers = models.ManyToManyField('self', blank=True, related_name="following")
    hugs_to_notify = models.ManyToManyField('Hug', blank=True)

    def __str__(self):
        return self.user.get_username()

    def hugs_come_and_gone(self):
        return Hug.objects.filter(models.Q(source=self.user) | models.Q(target=self.user)).order_by('-timestamp')

    def get_absolute_url(self):
        return reverse("user_page", kwargs=dict(username=self.user.username))


class Follow(models.Model):
    source = models.ForeignKey(User, related_name="following")
    target = models.ForeignKey(User, related_name="followers")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s -> %s" % (self.source, self.target)

    class Meta:
        unique_together = ('source', 'target'),


class HugKind(models.Model):
    name = models.CharField(max_length=20, db_index=True)
    verb = models.CharField(max_length=20, db_index=True)
    verb_tercery = models.CharField(max_length=20)
    past = models.CharField(max_length=30)

    def serialize(self) -> dict:
        return dict(noun=self.name, verb=self.verb, verb_third=self.verb_tercery, verb_past=self.past)

    def __str__(self):
        return self.name


class Hug(models.Model):
    source = models.ForeignKey(User, db_index=True, related_name="hugs_given")
    source_colour = RGBColorField(default=best_colour, colors=BEST_COLOURS)
    target = models.ForeignKey(User, db_index=True, related_name="hugs_gotten")
    target_colour = RGBColorField(default=best_colour, colors=BEST_COLOURS)
    kind = models.ForeignKey(HugKind, db_index=True, related_name="hugs")
    inspiration = models.ForeignKey('self', null=True, blank=True, related_name="kids")
    timestamp = models.DateTimeField(default=timezone.now)

    def serialize(self) -> dict:
        return dict(id=self.pk, source=self.source.username, target=self.target.username, source_colour=self.source_colour, target_colour=self.target_colour, kind=self.kind.serialize(), inspiration=self.inspiration.pk if self.inspiration else None)

    def publish(self):
        red = get_redis_connection("default")
        serial = dict(channel="global", content=self.serialize())
        red.publish("hugs", json.dumps(serial))
        for subber in User.objects.only('username').filter(models.Q(pk=self.target.pk)|models.Q(pk=self.source.pk)|models.Q(following__target=self.target)|models.Q(following__target=self.source)).distinct():
            serial["channel"] = subber.username
            red.publish("hugs", json.dumps(serial))
