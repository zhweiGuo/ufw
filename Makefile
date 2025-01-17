SRCS     = src/ufw $(wildcard src/*.py)
POTFILES = locales/po/ufw.pot
TMPDIR   = ./tmp
SNAPDIR  = ./snap-build
EXCLUDES = --exclude='.git*' --exclude='*~' --exclude='*.swp' --exclude='*.pyc' --exclude='debian' --exclude='ubuntu' --exclude='ufw_source.*' --exclude='tmp'
VERSION  = $(shell egrep '^ufw_version' ./setup.py | cut -d "'" -f 2)
SRCVER   = ufw-$(VERSION)
TARBALLS = ../tarballs
TARSRC   = $(TARBALLS)/$(SRCVER)
TARDST   = $(TARBALLS)/$(SRCVER).tar.gz
PYFLAKES = $(TMPDIR)/pyflakes.out

ifndef $(PYTHON)
export PYTHON=python3
endif

ifeq ($(PYTHON),python3)
export PYFLAKES_EXE = pyflakes3
else
export PYFLAKES_EXE = pyflakes
endif

all: snap-build
ifneq ($(SNAPCRAFT_PROJECT_NAME),ufw)
	# Use setup.py to install. See README for details
	set | grep SNAP
	exit 1
endif

snap-build: clean
ifneq ($(SNAPCRAFT_PROJECT_NAME),ufw)
	# Use setup.py to install. See README for details
	exit 1
endif
	git log --oneline -n 1
	mkdir $(SNAPDIR)
	python3 ./setup.py install --root=$(SNAPDIR) --install-layout=deb
	chmod 644 $(SNAPDIR)/etc/ufw/*.rules $(SNAPDIR)/etc/ufw/*.init $(SNAPDIR)/usr/share/ufw/iptables/*.rules
	sed -i 's/IPT_MODULES=.*/IPT_MODULES=""/g' $(SNAPDIR)/etc/default/ufw
	sed -i 's/IPT_SYSCTL=\(.*\)/IPT_SYSCTL="$$SNAP_DATA\1"/g' $(SNAPDIR)/etc/default/ufw
	sed -i 's,net/ipv4/tcp_sack=,#net/ipv4/tcp_sack=,g'  $(SNAPDIR)/etc/ufw/sysctl.conf
	chmod -R g-w $(SNAPDIR)
	mkdir $(SNAPDIR)/docs
	for manfile in `ls doc/*.8` ; do \
		page=$$(basename $$manfile); \
		manout=$(SNAPDIR)/docs/$$(basename -s .8 $$page); \
		echo "Creating $$page ... "; \
		LANG='C' MANWIDTH=80 man --warnings -E ascii doc/$$page | col -b > "$$manout"; \
	done; \
	for manfile in iptables ip6tables iptables-restore ip6tables-restore ; do \
		manout=$(SNAPDIR)/docs/$$(basename -s .8 $$manfile); \
		echo "Creating $$manfile ... "; \
		LANG='C' MANWIDTH=80 man --warnings -E ascii $$manfile | col -b > "$$manout"; \
	done; \
	cp -f ./tests/test-smoke-snap $(SNAPDIR)
	rm -f $(SNAPDIR)/usr/lib/python3/dist-packages/ufw/__pycache__/*
	rmdir $(SNAPDIR)/usr/lib/python3/dist-packages/ufw/__pycache__/
	# temporary until can build with core20
	sed -i 's#^iptables_dir = .*#iptables_dir = "/var/snap/ufw/current/bin"#g' $(SNAPDIR)/usr/lib/python3/dist-packages/ufw/common.py
	sed -i 's#for d in \["/sbin", "/bin",#for d in \["/var/snap/ufw/current/bin", "/sbin", "/bin",#g' $(SNAPDIR)/usr/lib/python3/dist-packages/ufw/util.py
	sed -i 's#^PATH="#PATH="$${DATA_DIR}/bin:#g' $(SNAPDIR)/lib/ufw/ufw-init-functions

install: snap-build
ifneq ($(SNAPCRAFT_PROJECT_NAME),ufw)
	# Use setup.py to install. See README for details
	exit 1
endif
ifndef DESTDIR
	# When SNAPCRAFT_PROJECT_NAME=ufw, DESTDIR must be set
	exit 1
endif
	cp -a $(SNAPDIR)/* $(DESTDIR)
	ln -sf /var/snap/ufw/current/usr/lib/python3/dist-packages/ufw/__pycache__ $(DESTDIR)/usr/lib/python3/dist-packages/ufw/__pycache__

translations: $(POTFILES)
$(POTFILES): $(SRCS)
	xgettext -d ufw -L Python -o $@ $(SRCS)

mo:
	make -C locales all

test:
	./run_tests.sh -s -i $(PYTHON)

unittest:
	./run_tests.sh -s -i $(PYTHON) unit

coverage:
	$(PYTHON) -m coverage run ./tests/unit/runner.py

coverage-report:
	$(PYTHON) -m coverage report --show-missing --omit="tests/*"

syntax-check: clean
	$(shell mkdir $(TMPDIR) && $(PYFLAKES_EXE) src 2>&1 | grep -v "undefined name '_'" > $(PYFLAKES))
	cat "$(PYFLAKES)"
	test ! -s "$(PYFLAKES)"

style-check: clean
ifeq (, $(shell which black))
	@echo "No black in '$(PATH)', skipping style check"
else
	black --check --diff --quiet ./src/*py ./src/ufw ./setup.py
endif

inclusivity-check: clean
ifeq (, $(shell which woke))
	@echo "No woke in '$(PATH)', skipping inclusivity check"
else
	woke --exit-1-on-failure .
endif

man-check: clean
	$(shell mkdir $(TMPDIR) 2>/dev/null)
	for manfile in `ls doc/*.8`; do \
		page=$$(basename $$manfile); \
		manout=$(TMPDIR)/$$page.out; \
		echo "Checking $$page for errors... "; \
		PAGER=cat LANG='en_US.UTF-8' MANWIDTH=80 man --warnings -E UTF-8 -l doc/$$page >/dev/null 2> "$$manout"; \
		cat "$$manout"; \
		test ! -s "$$manout" || exit 1; \
		echo "PASS"; \
	done; \

snap-test:
	$(shell mkdir $(TMPDIR) 2>/dev/null)
	./tests/test-srv-upgrades.sh > $(TMPDIR)/test-srv-upgrades.out 2>&1 && diff -Naur ./tests/test-srv-upgrades.sh.expected $(TMPDIR)/test-srv-upgrades.out

check: style-check syntax-check inclusivity-check man-check test unittest snap-test

# These are only used in development
clean:
	rm -rf ./build
	rm -rf ./staging
	rm -rf ./tests/testarea ./tests/unit/tmp
	rm -rf $(TMPDIR)
	rm -rf $(SNAPDIR)
	rm -rf ./parts ./stage ./prime
	rm -f ./locales/mo/*.mo
	rm -f ./tests/unit/*.pyc ./tests/*.pyc ./src/*.pyc
	rm -rf ./tests/unit/__pycache__ ./tests/__pycache__ ./src/__pycache__
	rm -rf ./.coverage
	rm -f ./ufw               # unittest symlink

evaluate: clean
	mkdir -p $(TMPDIR)/ufw/usr $(TMPDIR)/ufw/etc
	UFW_SKIP_CHECKS=1 $(PYTHON) ./setup.py install --home=$(TMPDIR)/ufw
	PYTHONPATH=$(PYTHONPATH):$(TMPDIR)/ufw/lib/python $(PYTHON) $(TMPDIR)/ufw/usr/sbin/ufw version
	cp ./examples/* $(TMPDIR)/ufw/etc/ufw/applications.d
	# Test with:
	# PYTHONPATH=$$PYTHONPATH:$(TMPDIR)/ufw/lib/python $(PYTHON) $(TMPDIR)/ufw/usr/sbin/ufw ...
	# sudo sh -c "PYTHONPATH=$$PYTHONPATH:$(TMPDIR)/ufw/lib/python $(PYTHON) $(TMPDIR)/ufw/usr/sbin/ufw ..."

devel: evaluate
	cp -f ./tests/defaults/profiles/* $(TMPDIR)/ufw/etc/ufw/applications.d
	cp -f ./tests/defaults/profiles.bad/* $(TMPDIR)/ufw/etc/ufw/applications.d

debug: devel
	sed -i 's/DEBUGGING = False/DEBUGGING = True/' $(TMPDIR)/ufw/lib/python/ufw/util.py

tarball: syntax-check clean translations
	cp -a . $(TARSRC)
	tar -zcv -C $(TARBALLS) $(EXCLUDES) -f $(TARDST) $(SRCVER)
	rm -rf $(TARSRC)
