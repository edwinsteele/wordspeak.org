#!/bin/sh

# Prerequisites for setup on a fedora 17 box.
# Should be run before pip install -r requirements.txt

# Must be root
if $(whoami) == "root";
then
  echo "This script must be not run as root, it gets root permissions via sudo. Exiting".
  exit 1;
fi

# To allow compilation of python modules
sudo yum install gcc python-devel

# To allow compilation of the enchant spell checker
sudo yum install enchant

# To allow compilation of lxml
sudo yum install libxmlt libxml-devel libxslt-devel

# Manually install Linkchecker. It doesn't install via pip because it's distributed as an xz archive
tempdir=$(mktemp -d)
wget http://github.com/downloads/wummel/linkchecker/LinkChecker-8.4.tar.xz -O $tempdir/LinkChecker-8.4.tar.xz
unxz $tempdir/LinkChecker-8.4.tar.xz
pip install $tempdir/Linkchecker-8.4.tar
rm -r $tempdir
