from django.test import TestCase

from .models import best_colour, BEST_COLOURS


class ColourTests(TestCase):

    def test_best_colour_in_best_colours(self):
        self.assertIn(best_colour(), BEST_COLOURS)


