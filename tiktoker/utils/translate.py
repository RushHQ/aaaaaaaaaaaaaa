import gettext
from os import walk, system, getcwd
import re
from iso639 import languages

# python .\utils\pygettext.py -d bot -o .\locale\en\LC_MESSAGES\bot.po .\bot.py
# example how to make po file

regex = r"Language-Team: (.*)"
_languages = [dir for dir in walk("./tiktoker/locale")][0][1]
language_names = {}

for lang in _languages:
    language_names[lang] = languages.get(alpha2=lang).name


def load_lang(file: str):
    """Load a language file"""
    for x in _languages:
        cwd = getcwd().replace("\\", "/")  # windows lol
        print("Loading {} for {}".format(file, x))
        system(
            "python "
            + cwd
            + "/tiktoker/utils/msgfmt.py "
            + cwd
            + "/tiktoker/locale/"
            + x
            + f"/LC_MESSAGES/{file}.po"
        )

    initilized_langs = {}

    for x in _languages:
        try:
            initilized_langs[x] = gettext.translation(
                file, "./tiktoker/locale", languages=[x]
            )
        except FileNotFoundError:
            continue

    for lang in _languages:
        try:
            initilized_langs[lang].install()
        except KeyError:
            continue

    return initilized_langs
