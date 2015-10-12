ufw

Netfilter firewall tool. Usage:
- make sure the iptable\_filter and ip6table\_filter modules are loaded using
  'snappy config ubuntu-core'
- to troubleshoot by running the commands directly out of /apps, be sure to
  use '--rootdir=/apps/ufw*/current --datadir=/var/lib/apps/ufw*/current' for
  the 'ufw' commenad and for the 'ufw-init' command,
  '--rootdir /apps/ufw*/current --datadir /var/lib/apps/ufw*/current"
