import json
import re
import subprocess

# /usr/bin/pacman -Qi docker-machine zuki-themes
OUTPUT = """\
Name            : docker-machine
Version         : 0.8.2-1
Description     : Machine management for a container-centric world
Architecture    : x86_64
URL             : https://github.com/docker/machine
Licenses        : Apache
Groups          : None
Provides        : None
Depends On      : gcc-libs
Optional Deps   : net-tools: required for VirtualBox driver [installed]
Required By     : None
Optional For    : None
Conflicts With  : None
Replaces        : None
Installed Size  : 56.28 MiB
Packager        : Felix Yan <felixonmars@archlinux.org>
Build Date      : Thu 20 Oct 2016 11:17:18 BST
Install Date    : Thu 20 Oct 2016 19:42:22 BST
Install Reason  : Explicitly installed
Install Script  : No
Validated By    : Signature

Name            : zuki-themes
Version         : 20150516-1
Description     : Zuki themes for GTK3, GTK2, Metacity, xfwm4, Gnome Shell and
                  Unity.
Architecture    : any
URL             : https://github.com/lassekongo83/zuki-themes/
Licenses        : GPL3
Groups          : None
Provides        : None
Depends On      : gtk-engine-murrine  gtk-engines  gnome-themes-standard
Optional Deps   : ttf-droid: Font family for the Gnome Shell theme [installed]
Required By     : None
Optional For    : None
Conflicts With  : None
Replaces        : zukitwo-themes
Installed Size  : 2.48 MiB
Packager        : Antergos Build Server <dev@antergos.com>
Build Date      : Sat 16 May 2015 17:23:08 BST
Install Date    : Sun 02 Oct 2016 14:48:06 BST
Install Reason  : Explicitly installed
Install Script  : No
Validated By    : SHA-256 Sum"""

def parse_pacman_qi(output, captions=('Name', 'Version', 'Description', 'Architecture', 'URL')):
    """
    Takes a multiline string as input

    Returns a list of dictionaries pertaining to the output
    with keys matching the captions passed as input.
    """
    packages = []
    # group packages together
    for package in output.split('\n\n'):
        caption = ""
        current_package = {}
        # each line in the package grouping
        for line in package.split('\n'):
            # match initial line e.g. Caption  : Info
            info = re.match(r'^([A-Za-z]+)\s*:\s+(.*)$', line)
            if info:
                # if its a definition, add to the dict
                caption = info.group(1)
                current_package[caption] = info.group(2)
            else:
                # is it a continuation of a caption,
                # i.e. zuki-themes description 2nd line
                info = re.match(r'^\s+(.*)$', line)
                if info and caption:
                    # append the info to the respective caption
                    current_package[caption] += ' ' + info.group(1)
                elif not caption:
                    # no caption has been defined so this is stray output
                    raise ValueError("Malformed pacman output")

        # add the related info to the packages list as a dict
        # with only relevant captions, using a dict comprehension
        packages.append({
            caption: value for caption, value in current_package.items()
            if caption in captions
        })

    return packages

# replace OUTPUT with however you're obtaining pacman output
# e.g.
# import subprocess
output = subprocess.getoutput("pacman -Qi")

packages = parse_pacman_qi(output)

print("Sending {} packages: {}...".format(
    len(packages),
    ", ".join(package['Name'] for package in packages),
))

json_dict = {"packages": packages}
print(json.dumps(json_dict))
