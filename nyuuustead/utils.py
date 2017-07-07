from django.contrib.auth.models import User

from nyuuustead.models import Userware, best_colour, Pronoun


def assert_userware(user: User, suggested_colour=None):
    try:
        user.userware
    except Userware.DoesNotExist:
        Userware.objects.create(user=user, colour=suggested_colour, pronoun=Pronoun.objects.get(reflexive="themself"))


class UserwareMiddleware(object):
    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            assert_userware(request.user, request.session.get("colour", best_colour()))
        else:
            if "colour" not in request.session:
                request.session["colour"] = best_colour()
        return None
