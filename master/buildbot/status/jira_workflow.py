# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members
# Copyright 2013 (c) Mamba Team

"""Push build events to Jira issues workflow.
"""

import re
try:
    import json
    assert json
except ImportError:
    import simplejson as json

from twisted.python import log
from twisted.web import client
from twisted.internet import defer
from buildbot.status.base import StatusReceiverMultiService


class JiraWorkflowStatusPush(StatusReceiverMultiService):

    """
    Event streamer to Jira issues workflow.

    This status notifier needs the commit messages are built in a specific
    way. By default the JIRA integration with the most popular DVCS (Github
    and BitBucket) already needs some extra commit special messages
    """

    def __init__(self, host, user, password, api_ver, builder, **kwargs):

        StatusReceiverMultiService.__init__(self)

        self.host = host
        self.user = user
        self.password = password
        self.api_ver = api_ver
        self.builder = builder
        self.regex = re.compile(r'(?:\s|^)([A-Z]+-[0-9]+)(?=\s|$)')

    def startService(self):
        """Start the service up
        """

        log.msg('Starting JIRA Workflow')
        StatusReceiverMultiService.startService(self)
        self.status = self.parent.getStatus()
        self.status.subscribe(self)

    def builderAdded(self, name, builder):
        return self  # subscribe to this builder

    @defer.inlineCallbacks
    def buildStarted(self, builder_name, build):
        """Called when the build is started
        """

        data = build.asDict()
        if (not self.check_builder(data, build)
                or len(data['sourceStamps']) == 0):
            return

        for stamp in data['sourceStamps']:
            if len(stamp['changes']) == 0:
                continue

            for change in stamp['changes']:
                jira_issues = set(self.regex.findall(change['comments']))

    def buildFinished(self, builder_name, build):
        pass

    def send_request_to_jira(self):
        pass

    def check_builder(self, data, build):
        """Determine if the builder used is the builder we allow
        """

        return data['builderName'] in self.builder
