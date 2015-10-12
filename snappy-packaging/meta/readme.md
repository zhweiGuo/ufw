ufw

Netfilter firewall tool. Usage:

First make sure that the iptable_filter and ip6table_filter modules are loaded:
1. $ snappy config ubuntu-core > ./config
2. adjust ./config to have this:
   config:
     ubuntu-core:
       modules-load: iptable_filter ip6table_filter
3. $ sudo snappy config ubuntu-core ./config

Now you can use the 'ufw.cli' tool to manipulate the firewall. Eg:
$ sudo ufw.cli allow 22/tcp
$ sudo ufw.cli enable

At this point, the firewall is enabled, allows TCP port 22 (ssh) and will start
on boot. To disable:

$ sudo ufw.cli disable

The 'ufw.init' tool is also available for troubleshooting (it is used to start
the firewall on boot).

For more information, see https://wiki.ubuntu.com/UncomplicatedFirewall

Please file bugs at: https://bugs.launchpad.net/ufw/+filebug

TODO:
- add check-requirements as a binary
- adjust ufw-init to take '--rootdir=foo' instead of '--rootdir foo'
