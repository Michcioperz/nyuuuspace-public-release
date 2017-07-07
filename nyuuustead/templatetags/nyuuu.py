import colorsys

from django import template
from django.contrib.auth.models import User

from nyuuustead.models import best_colour

register = template.Library()


@register.filter
def followed_by(target: User, source: User) -> bool:
    return target.followers.filter(source=source).exists()


def colour_optimizer(colour: str) -> str:
    if colour is None or len(colour) < 7:
        colour = best_colour()
    col = [float(int(x, 16))/255 for x in [colour[1:3], colour[3:5], colour[5:7]]]
    hls = list(colorsys.rgb_to_hls(*col))
    hls[1] = min(hls[1], 0.8)
    rgb = colorsys.hls_to_rgb(*hls)
    return "#"+"".join([str(hex(int(x*255)))[2:].rjust(2, '0') for x in rgb])


register.filter("colour_optimizer", colour_optimizer)


def bright_detector(colour: str) -> bool:
    if colour is None or len(colour) < 7:
        colour = best_colour()
    col = [float(int(x, 16))/255 for x in [colour[1:3], colour[3:5], colour[5:7]]]
    return colorsys.rgb_to_hls(*col)[1] > 0.8


register.filter("bright_detector", bright_detector)
