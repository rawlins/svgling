import os, os.path, shutil

def copy_changelog():
    here = os.path.dirname(os.path.realpath(__file__))
    there = os.path.join(here, "..", "CHANGELOG.md")
    target = os.path.join(here, "CHANGELOG.md")

    # using copy2 here has very odd effects on quarto?
    if not os.path.exists(target) or os.stat(there).st_mtime - os.stat(target).st_mtime > 1:
        shutil.copy(there, here)

# the changelog is best kept in the main repo directory, but it is helpful to
# show it on the website also. This script simply copies it over, I didn't find
# a better way to to this in quarto.
# Note: there is a weirdness on initial render that currently makes this fail
# on the first rendering pass; to generate a website in one pass, manually
# run this script first. See:
# https://github.com/quarto-dev/quarto-cli/discussions/3879
copy_changelog()
