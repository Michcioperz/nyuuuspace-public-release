from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST, require_GET

from registration.forms import RegistrationFormUniqueEmail, RegistrationFormNoFreeEmail

from nyuuustead.templatetags.nyuuu import colour_optimizer, bright_detector
from .models import HugKind, Hug, Userware, Follow, best_colour
from .utils import assert_userware


def main_page(request):
    if request.user.is_authenticated():
        # query = Q(source=request.user) | Q(target=request.user)
        # for follow in request.user.userware.following.select_related('user').all():
        #     query |= Q(source=follow.user) | Q(target=follow.user)
        return render(request, "main.html", dict(stream=Hug.objects.filter(
            Q(source=request.user) | Q(target=request.user) |
            Q(source__followers__source=request.user) |
            Q(target__followers__source=request.user)).distinct().order_by('-timestamp')[:20],
                                                 followables=User.objects.select_related('userware').filter(
                                                     Q(is_active=True) & ~Q(pk=request.user.pk) & ~Q(
                                                         followers__source=request.user)).order_by('?')[:3]))
    else:
        return render(request, "landing.html")
        # return render(request, "error.html", dict(error_content='<p>We are currently <ruby st' +
        #                                                        'yle="ruby-position:under;ruby-merge:auto;ruby-align' +
        #                                                        ':center"><rb>頑<rb>張<rb>っ<rb>て</rb><rtc lang="en" st' +
        #                                                        'yle="font-size:1rem;font-weight:200"><rt>gan<rt>b' +
        #                                                       'a<rt>t<rt>te</rt></rtc></ruby>ing to get Nyuuuspace ' +
        #                                                        'done.</p><p>Please come back soon!</p>'))


def global_feed(request):
    return render(request, "global.html", dict(stream=Hug.objects.order_by('-timestamp')[:40]))


class HugKindForm(forms.Form):
    kind = forms.ModelChoiceField(HugKind.objects, to_field_name="verb", initial="hug")


class TrueRegistrationForm(RegistrationFormUniqueEmail, RegistrationFormNoFreeEmail):
    bad_domains = ['mailinator.com', 'mvrht.com']

    def __init__(self, *args, **kwargs):
        super(TrueRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = "Required. 30 characters or fewer. Letters, digits and @/+/-/_ only."

    def clean_username(self):
        uname = self.cleaned_data.get('username')
        if '.' in uname:
            raise forms.ValidationError("You can't have a dot in your username, sorry!")
        if User.objects.filter(username__iexact=uname).exists():
            raise forms.ValidationError('There is already a user going by this name!')
        return self.cleaned_data.get('username')


def user_page(request, username):
    try:
        target = User.objects.select_related("userware").filter(is_active=True).get(username__iexact=username)
        assert_userware(target)
        if request.method == 'POST':
            if not request.user.is_authenticated():
                messages.add_message(request, messages.ERROR, "You have to log in to hug!")
                try:
                    assert is_safe_url(request.POST['next'], "nyuuu.space")
                    return redirect(request.POST['next'])
                except (AssertionError, KeyError):
                    return redirect('auth_login')
            if not request.user.is_active:
                messages.add_message(request, messages.ERROR, "Your account is not active yet!")
                try:
                    assert is_safe_url(request.POST['next'], "nyuuu.space")
                    return redirect(request.POST['next'])
                except (AssertionError, KeyError):
                    return redirect(target.userware)
            form = HugKindForm(request.POST)
            if form.is_valid():
                new_hug = Hug.objects.create(source=request.user, source_colour=request.user.userware.colour,
                                             target=target,
                                             target_colour=target.userware.colour,
                                             kind=form.cleaned_data.get("kind", 1))
                new_hug.publish()
                target.userware.hugs_to_notify.add(new_hug)
                messages.add_message(request, messages.SUCCESS,
                                     "%s %s!" % (target.username, form.cleaned_data.get("kind").past))
                try:
                    assert is_safe_url(request.POST['next'], "nyuuu.space")
                    return redirect(request.POST['next'])
                except (AssertionError, KeyError):
                    return redirect(target.userware)
            else:
                messages.add_message(request, messages.ERROR, "We didn't recognize your hug kind of choice!")
                try:
                    assert is_safe_url(request.POST['next'], "nyuuu.space")
                    return redirect(request.POST['next'])
                except (AssertionError, KeyError):
                    return redirect(target.userware)
        form = HugKindForm()
        return render(request, "user_page.html", dict(target=target, form=form))
    except User.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find a huggable user going by this username"))


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Userware
        fields = 'pronoun', 'daily_notifications', 'hourly_notifications', 'news_emails', 'colour'


@login_required
def settings_page(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=request.user.userware)
        form.user = request.user
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings were saved! <3")
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, "%s: %s" % (field, error))
    else:
        form = SettingsForm(instance=request.user.userware)
    return render(request, "settings.html", dict(form=form))


@require_POST
@login_required
def user_follow_action(request, username: str):
    try:
        target = User.objects.get(is_active=True, username__iexact=username)
        Follow.objects.get_or_create(source=request.user, target=target)
        messages.add_message(request, messages.SUCCESS, "%s followed!" % target.username)
        try:
            assert is_safe_url(request.POST['next'], "nyuuu.space")
            return redirect(request.POST['next'])
        except (AssertionError, KeyError):
            return redirect(reverse("user_page", kwargs=dict(username=target.username)))
    except User.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find a huggable user going by this username"))


@require_POST
@login_required
def user_unfollow_action(request, username: str):
    try:
        target = User.objects.get(is_active=True, username__iexact=username)
        Follow.objects.filter(source=request.user, target=target).delete()
        messages.add_message(request, messages.SUCCESS, "%s unfollowed!" % target.username)
        try:
            assert is_safe_url(request.POST['next'], "nyuuu.space")
            return redirect(request.POST['next'])
        except (AssertionError, KeyError):
            return redirect(reverse("user_page", kwargs=dict(username=target.username)))
    except User.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find a huggable user going by this username"))


def hug_page(request, ident: str):
    ident = int(ident)
    try:
        hug = Hug.objects.get(pk=ident)
        return render(request, "hug_page.html", dict(hug=hug))
    except Hug.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find the relevant hug"))


@require_POST
@login_required
def hug_rehug_action(request, ident: str):
    ident = int(ident)
    try:
        hug = Hug.objects.select_related('target', 'target__userware').get(pk=ident)
        new_hug = Hug.objects.create(source=request.user, source_colour=request.user.userware.colour, target=hug.target,
                                     target_colour=hug.target.userware.colour, kind=hug.kind, inspiration=hug)
        new_hug.publish()
        new_hug.target.userware.hugs_to_notify.add(new_hug)
        messages.add_message(request, messages.SUCCESS, "%s re%s!" % (hug.target.username, hug.kind.past))
        try:
            assert is_safe_url(request.POST['next'], "nyuuu.space")
            return redirect(request.POST['next'])
        except (AssertionError, KeyError):
            return redirect(reverse("hug_page", kwargs=dict(ident=str(new_hug.pk))))
    except Hug.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find the relevant hug"))


@require_POST
@login_required
def hug_hugback_action(request, ident: str):
    ident = int(ident)
    try:
        hug = Hug.objects.select_related('source', 'source__userware').get(pk=ident)
        new_hug = Hug.objects.create(source=request.user, source_colour=request.user.userware.colour, target=hug.source,
                                     target_colour=hug.source.userware.colour, kind=hug.kind, inspiration=hug)
        new_hug.publish()
        new_hug.target.userware.hugs_to_notify.add(new_hug)
        messages.add_message(request, messages.SUCCESS, "%s %s back!" % (hug.source.username, hug.kind.past))
        try:
            assert is_safe_url(request.POST['next'], "nyuuu.space")
            return redirect(request.POST['next'])
        except (AssertionError, KeyError):
            return redirect(reverse("hug_page", kwargs=dict(ident=new_hug.pk)))
    except Hug.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find the relevant hug"))


@require_GET
@login_required
def hug_rehug_question(request, ident: str):
    ident = int(ident)
    try:
        hug = Hug.objects.get(pk=ident)
        context = dict(hug=hug, action=reverse("hug_rehug_action", kwargs=dict(ident=ident)),
                       behavior=" ".join(("re" + hug.kind.verb, hug.target.username)))
        if 'HTTP_REFERER' in request.META and is_safe_url(request.META['HTTP_REFERER'], 'nyuuu.space'):
            context['next'] = request.META['HTTP_REFERER']
        return render(request, "question.html", context)
    except Hug.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find the relevant hug"))


@require_GET
@login_required
def hug_hugback_question(request, ident: str):
    ident = int(ident)
    try:
        hug = Hug.objects.get(pk=ident)
        context = dict(hug=hug, action=reverse("hug_hugback_action", kwargs=dict(ident=ident)),
                       behavior=" ".join((hug.kind.verb, hug.source.username, "back")))
        if 'HTTP_REFERER' in request.META and is_safe_url(request.META['HTTP_REFERER'], 'nyuuu.space'):
            context['next'] = request.META['HTTP_REFERER']
        return render(request, "question.html", context)
    except Hug.DoesNotExist:
        return render(request, "error.html", status=404,
                      context=dict(error_content="We couldn't find the relevant hug"))


@require_GET
@cache_page(60 * 15)
def users_search(request, query: str):
    return JsonResponse(data=dict(error=None, users=[
        dict(username=x.username,
             colour=colour_optimizer(x.userware.colour if hasattr(x, 'userware') else best_colour()),
             overbright=bright_detector(x.userware.colour) if hasattr(x, 'userware') else False) for x in
        User.objects.filter(is_active=True, username__icontains=query).order_by("username")]))


@require_GET
def users_search_page(request):
    return render(request, "users_search.html")
