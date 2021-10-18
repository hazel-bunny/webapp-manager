import os
import re
from subprocess import Popen
from pathlib import Path
import configparser
config = configparser.ConfigParser()

class Build():
    def __init__(self, title, url, icon, category):
        self.title = title
        self.package_name = f"{re.sub('[^A-Za-z]+', '', title.lower())}-jak-webapp"
        self.build_path = f"/tmp/webapp/{self.package_name}/"
        self.url = url
        self.category = category
        self.icon = icon

    def find_pkg(self):
        version = "-1.0-1-any"
        paths = (
            f"{str(Path.home())}/makepkg.conf",
            "/etc/makepkg.conf"
            )
        for path in paths:
            if os.path.exists(path):
                with open(path) as f:
                    sec = '[section]\n' + f.read()
                    config.read_string(sec)
                    bp = config["section"]["PKGDEST"]
                    pe = config["section"]["PKGEXT"]
                    if not bp.endswith("/"):
                        bp = bp + "/"
                    if os.path.isfile(f"{bp}{self.package_name}{version}{pe}"):
                        self.build_path = bp
                        pkg_ext = pe
                        break
                    else:
                        pkg_ext = ".pkg.tar.zst"
            else:
                pkg_ext = ".pkg.tar.zst"

        return f"{self.build_path}{self.package_name}{version}{pkg_ext}"


    def build_desktop(self):
        with open(self.build_path + f"{self.package_name}.desktop", 'w+') as desktop_file:
            desktop_file.write("[Desktop Entry]\n")
            desktop_file.write("Version=1.0\n")
            desktop_file.write("Name=%s\n" % self.title)
            desktop_file.write("Comment=User made web app\n")
            desktop_file.write("Terminal=false\n")
            desktop_file.write("Type=Application\n")
            desktop_file.write("Icon=%s\n" % self.icon)
            desktop_file.write("Categories=GTK;%s;\n" % self.category)
            desktop_file.write("StartupNotify=true\n")
            desktop_file.write("Exec=" + f"bash -c 'jak-cli --url {self.url}  --title {self.title}'")

    def build_package(self):
        with open(self.build_path + "PKGBUILD", 'w+') as pkgbuild:
           pkgbuild.write(f"pkgname={self.package_name}" + "\n")
           pkgbuild.write("pkgver=1.0\n")
           pkgbuild.write("pkgrel=1\n")
           pkgbuild.write("pkgdesc='User made web app'\n")
           pkgbuild.write("arch=('any')\n")
           pkgbuild.write("license=('GPL')\n")
           pkgbuild.write(f"url='{self.url}'" + "\n")
           pkgbuild.write(f"source=('{self.package_name}.desktop')" + "\n")
           pkgbuild.write("md5sums=('SKIP')\n")
           pkgbuild.write("""package() {
               mkdir -p $pkgdir/usr/share/applications
               cp "$srcdir/%s.desktop" $pkgdir/usr/share/applications
           }""" % self.package_name
           ) 
        p = Popen([f"cd {self.build_path} && makepkg"], shell=True)
        p.wait()
        
    def install_package(self):
        Popen(["pamac-installer", self.find_pkg()])
        
    def start(self):
        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)
        self.build_desktop()
        self.build_package()
        self.install_package()
        
