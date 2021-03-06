# Copyright (C) 2013 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-dbfixtures.

# pytest-dbfixtures is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-dbfixtures is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-dbfixtures.  If not, see <http://www.gnu.org/licenses/>.
"""PostgreSQL executor crafter around pg_ctl."""

import re
import subprocess

from pytest_dbfixtures.executors import TCPExecutor


class PostgreSQLExecutor(TCPExecutor):

    """
    PostgreSQL executor running on pg_ctl.

    Based over an `pg_ctl program
    <http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html>`_
    """

    BASE_PROC_START_COMMAND = """{pg_ctl} start -D {datadir}
    -o "-F -p {port} -c %s='{unixsocketdir}'" -l {logfile} {startparams}"""

    PROC_START_COMMAND = {
        '8.4': BASE_PROC_START_COMMAND % 'unix_socket_directory',
        '9.0': BASE_PROC_START_COMMAND % 'unix_socket_directory',
        '9.1': BASE_PROC_START_COMMAND % 'unix_socket_directory',
        '9.2': BASE_PROC_START_COMMAND % 'unix_socket_directory',
        '9.3': BASE_PROC_START_COMMAND % 'unix_socket_directories',
        '9.4': BASE_PROC_START_COMMAND % 'unix_socket_directories',
    }

    def __init__(self, pg_ctl, host, port,
                 datadir, unixsocketdir, logfile, startparams,
                 shell=False, timeout=None, sleep=0.1):
        """
        Initialize PostgreSQLExecutor executor.

        :param str pg_ctl: pg_ctl location
        :param str host: host under which process is accessible
        :param int port: port under which process is accessible
        :param str datadir: path to postgresql datadir
        :param str unixsocketdir: path to socket directory
        :param str logfile: path to logfile for postgresql
        :param str startparams: additional start parameters
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        """
        self.pg_ctl = pg_ctl
        self.version = self.version()
        self.datadir = datadir
        self.unixsocketdir = unixsocketdir
        command = self.PROC_START_COMMAND[self.version].format(
            pg_ctl=self.pg_ctl,
            datadir=self.datadir,
            port=port,
            unixsocketdir=self.unixsocketdir,
            logfile=logfile,
            startparams=startparams,
        )
        super(PostgreSQLExecutor, self).__init__(
            command, host, port, shell=shell, timeout=timeout, sleep=sleep)

    def version(self):
        """Detect postgresql version."""
        version_string = subprocess.check_output(
            [self.pg_ctl, '--version']).decode('utf-8')
        matches = re.search('.* (?P<version>\d\.\d)\.\d', version_string)
        return matches.groupdict()['version']

    def running(self):
        """Check if server is still running."""
        output = subprocess.check_output(
            '{pg_ctl} status -D {datadir}'.format(
                pg_ctl=self.pg_ctl,
                datadir=self.datadir
            ),
            shell=True
        ).decode('utf-8')
        return "pg_ctl: server is running" in output

    def stop(self):
        """Issues a stop request to pg_ctl"""
        subprocess.check_output(
            '{pg_ctl} stop -D {datadir} -m f'.format(
                pg_ctl=self.pg_ctl,
                datadir=self.datadir,
                port=self.port,
                unixsocketdir=self.unixsocketdir
            ),
            shell=True)
