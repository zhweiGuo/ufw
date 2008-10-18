SRCS     = src/ufw $(wildcard src/*.py)
POTFILES = messages/ufw.pot
TMPDIR   = ./tmp
EXCLUDED = --exclude='.bzr*' --exclude='*~' --exclude='*.swp' --exclude='*.pyc' --exclude='build'
VERSION  = $(shell egrep '^ufw_version' ./setup.py | cut -d "'" -f 2)

translations: $(POTFILES)
$(POTFILES): $(SRCS)
	pygettext -v -d ufw -p messages -S GNU $(SRCS)

test:
	./run_tests.sh -s

all:
	# Use setup.py to install. See README for details
	exit 1

install: all

# These are only used in development
clean:
	rm -rf $(TMPDIR)/ufw

evaluate: clean
	mkdir -p $(TMPDIR)/ufw/usr $(TMPDIR)/ufw/etc
	python ./setup.py install --home=$(TMPDIR)/ufw
	sed -i 's/self.do_checks = True/self.do_checks = False/' $(TMPDIR)/ufw/lib/python/ufw/backend.py
	cp ./examples/* $(TMPDIR)/ufw/etc/ufw/applications.d

devel: evaluate
	cp -f ./tests/defaults/profiles/* $(TMPDIR)/ufw/etc/ufw/applications.d
	cp -f ./tests/defaults/profiles.bad/* $(TMPDIR)/ufw/etc/ufw/applications.d

debug: devel
	sed -i 's/debugging = False/debugging = True/' $(TMPDIR)/ufw/lib/python/ufw/util.py

tarball:
	mkdir ufw-$(VERSION)
	cp -a ./* ufw-$(VERSION)
	tar -zcv --exclude='.bzr*' --exclude='*~' --exclude='*.swp' --exclude='*.pyc' --exclude='build' -f ufw-$(VERSION).tar.gz ufw-$(VERSION)
	rm -rf ufw-$(VERSION)

