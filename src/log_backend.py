"""log_backend.py: interface for ufw logging backend"""
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

from ufw.common import UFWError


class UFWLogBackend:
    """Interface for logging backend"""

    own_logging_options = ""

    def __init__(self, logging_additional=None):
        if logging_additional is None:
            self.additional_options = []
        else:
            self.additional_options = filter(
                lambda x: x != self.own_logging_options, logging_additional.split(","),
            )

    def get_log_target(self):
        """Return what is the logging target for the backend"""
        raise UFWError("UFWLogBackend:get_log_target: need to override")

    def get_logging_options(self):
        """Return the logging options for this logging backend"""
        ret = []
        ret.extend(self.additional_options)
        ret.append(self.own_logging_options)
        return ret
