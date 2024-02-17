"""kernel_log_backend.py: backend for kernel (LOG) based logging in ufw"""
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


class UFWLogBackendKernel(ufw.log_backend.UFWLogBackend):
    """Instance class for UFWLogBackend"""

    own_logging_options = "--log-prefix"

    def __init__(self):
        ufw.log_backend.UFWLogBackend.__init__(self)

    def get_log_target(self):
        return "LOG"
