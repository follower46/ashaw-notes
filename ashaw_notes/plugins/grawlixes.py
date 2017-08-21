""" Expletives Replacement
    This allows me to write spicy notes
"""
import re
from ashaw_notes.plugins import base_plugin


class Plugin(base_plugin.Plugin):
    """Date Handler Plugin Class"""

    regex = re.compile(
        '(' \
        '(\\bfuck(ed|er|ers|up|ing|s|tard|fest|head|heads|ildoo)?\\b)' \
        '|(\\bshit(ted|ter|ters|ting|s|head|heads|face|show|storm|squirtles)?\\b)' \
        '|(\\bbitch(y|ing|es|izzles)?\\b)' \
        '|(\\bdamn(s|ing|it|alamadingdong)?\\b)' \
        '|(\\bcrap(s|per|pers|ping|cakes|fest|sickles)?\\b)' \
        '|(\\bass(es|wipe|hat|hats|hole|holes)?\\b)' \
        '|(\\bhell\\b)' \
        '|(\\bscrew(ed)?\\b)' \
        '|(\\biboubi(d)?\\b)' \
        ')'
    )

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        style = 'color:#ccc;' \
        'font-weight:bold;' \
        'text-transform:uppercase;'
        note_line = Plugin.regex.sub(
            r'<span style="' + style + r'" title="\1">@#$%\3</span>',
            note_line)
        return note_line
