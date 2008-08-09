all:
	# Use setup.py to install. See README for details
	exit 1

install: all

test:
	run_tests -s

clean:
	rm -rf /tmp/ufw

evaluate: clean
	mkdir -p /tmp/ufw/usr /tmp/ufw/etc
	python ./setup.py install --home=/tmp/ufw
	sed -i 's/self.do_checks = True/self.do_checks = False/' /tmp/ufw/lib/python/ufw/backend.py
	cp ./examples/* /tmp/ufw/etc/ufw/applications.d

devel: evaluate
	cp -f ./tests/defaults/profiles/* /tmp/ufw/etc/ufw/applications.d
	cp -f ./tests/defaults/profiles.bad/* /tmp/ufw/etc/ufw/applications.d

debug: devel
	sed -i 's/debugging = False/debugging = True/' /tmp/ufw/lib/python/ufw/util.py

