""" This will generate the po files for english locale """
# Meant for manual use
# Should be ran from the root of the project

from os import walk, system, getcwd
import re

cwd = getcwd().replace("\\", "/")

scales = [dir for dir in walk("./tiktoker/scales")][0][2]

for x in scales:
    with open(cwd + "/tiktoker/scales/" + x, "r", encoding="UTF-8") as f:
        content = f.read()
        file_domain = re.findall(
            r"load_lang\(\"(?P<file_domain>\w*)\"\)", content, re.MULTILINE
        )[0]

    if not file_domain:
        continue

    system(
        "python "
        + cwd
        + f"/tiktoker/utils/pygettext.py -d {file_domain} -o "
        + cwd
        + f"/tiktoker/locale/en/LC_MESSAGES/{file_domain}.po {cwd}/tiktoker/scales/{x}"
    )
