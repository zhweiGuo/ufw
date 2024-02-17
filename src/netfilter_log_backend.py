"""netfilter_log_backend.py: backend for netfilter (NFLOG) based logging in ufw"""
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import ufw.log_backend


class UFWLogBackendNetfilter(ufw.log_backend.UFWLogBackend):
    """Instance class for UFWLogBackend"""

    own_logging_options = "--nflog-prefix"

    def __init__(self, additional_logging_options=None):
        ufw.log_backend.UFWLogBackend.__init__(self, additional_logging_options)

    def get_log_target(self):
        return "NFLOG"
