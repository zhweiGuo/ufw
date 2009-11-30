SRCS     = src/ufw $(wildcard src/*.py)
POTFILES = locales/po/ufw.pot
TMPDIR   = ./tmp
EXCLUDES = --exclude='.bzr*' --exclude='*~' --exclude='*.swp' --exclude='*.pyc' --exclude='debian' --exclude='ubuntu'
VERSION  = $(shell egrep '^ufw_version' ./setup.py | cut -d "'" -f 2)
SRCVER   = ufw-$(VERSION)
TARBALLS = ../tarballs
TARSRC   = $(TARBALLS)/$(SRCVER)
TARDST   = $(TARBALLS)/$(SRCVER).tar.gz

all:
	# Use setup.py to install. See README for details
	exit 1

install: all

translations: $(POTFILES)
$(POTFILES): $(SRCS)
	xgettext -d ufw -L Python -o $@ $(SRCS)

mo:
	make -C locales all

test:
	./run_tests.sh -s


# These are only used in development
clean:
	rm -rf ./build
	rm -rf ./staging
	rm -rf ./tests/testarea
	rm -rf $(TMPDIR)

evaluate: clean
	mkdir -p $(TMPDIR)/ufw/usr $(TMPDIR)/ufw/etc
	python ./setup.py install --home=$(TMPDIR)/ufw
	PYTHONPATH=$(PYTHONPATH):$(TMPDIR)/ufw/lib/python $(TMPDIR)/ufw/usr/sbin/ufw version
	sed -i 's/self.do_checks = True/self.do_checks = False/' $(TMPDIR)/ufw/lib/python/ufw/backend.py
	cp ./examples/* $(TMPDIR)/ufw/etc/ufw/applications.d
	# Test with:
	# PYTHONPATH=$$PYTHONPATH:$(TMPDIR)/ufw/lib/python $(TMPDIR)/ufw/usr/sbin/ufw ...
	# sudo sh -c "PYTHONPATH=$$PYTHONPATH:$(TMPDIR)/ufw/lib/python $(TMPDIR)/ufw/usr/sbin/ufw ..."

devel: evaluate
	cp -f ./tests/defaults/profiles/* $(TMPDIR)/ufw/etc/ufw/applications.d
	cp -f ./tests/defaults/profiles.bad/* $(TMPDIR)/ufw/etc/ufw/applications.d

debug: devel
	sed -i 's/debugging = False/debugging = True/' $(TMPDIR)/ufw/lib/python/ufw/util.py

tarball: clean translations
	bzr export --format dir $(TARSRC)
	tar -zcv -C $(TARBALLS) $(EXCLUDES) -f $(TARDST) $(SRCVER)
	rm -rf $(TARSRC)

