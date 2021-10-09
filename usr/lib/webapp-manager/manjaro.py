import os
import re
from subprocess import Popen


class Build():
    def __init__(self, name, url, icon, category):
        self.build_path = f"/tmp/webapp/{re.sub('[^A-Za-z]+', '', name)}-jak/"
        self.name = name
        self.url = url
        self.category = category
        self.icon = icon

    def build_desktop(self):
        name = re.sub('[^A-Za-z]+', '', self.name.lower())
        with open(self.build_path + f"{name}-jak.desktop", 'w+') as desktop_file:
            desktop_file.write("[Desktop Entry]\n")
            desktop_file.write("Version=1.0\n")
            desktop_file.write("Name=%s\n" % self.name)
            desktop_file.write("Comment=User made web app\n")
            desktop_file.write("Terminal=false\n")
            desktop_file.write("Type=Application\n")
            desktop_file.write("Icon=%s\n" % self.icon)
            desktop_file.write("Categories=GTK;%s;\n" % self.category)
            desktop_file.write("StartupNotify=true\n")
            desktop_file.write("Exec=" + f"bash -c 'jak-cli --url {self.url}  --title {self.name}'")

    def build_package(self):
        with open(self.build_path + "PKGBUILD", 'w+') as pkgbuild:
           name = re.sub('[^A-Za-z]+', '', self.name.lower())
           pkgbuild.write(f"pkgname={name}-web-jak" + "\n")
           pkgbuild.write("pkgver=1.0\n")
           pkgbuild.write("pkgrel=1\n")
           pkgbuild.write("pkgdesc='User made web app'\n")
           pkgbuild.write("arch=('any')\n")
           pkgbuild.write("license=('GPL')\n")
           pkgbuild.write(f"url='{self.url}'" + "\n")
           pkgbuild.write(f"source=('{name}-jak.desktop')" + "\n")
           pkgbuild.write("md5sums=('SKIP')\n")
           pkgbuild.write("""package() {
               mkdir -p $pkgdir/usr/share/applications
               cp "$srcdir/%s-jak.desktop" $pkgdir/usr/share/applications
           }""" % name
           ) 
        p = Popen([f"cd {self.build_path} && makepkg"], shell=True)
        p.wait()
        
    def install_package(self):
        name = re.sub('[^A-Za-z]+', '', self.name.lower())
        Popen(["pamac-installer", f"{self.build_path}{name}-web-jak-1.0-1-any.pkg.tar.zst"])      
        
    def start(self):
        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)
        self.build_desktop()
        self.build_package()
        self.install_package()
        
