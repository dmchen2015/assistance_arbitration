#!/usr/bin/env python
# The main action server that provides the remote recovery behaviours

from __future__ import print_function, division

import os
import pickle
import subprocess

import rospy
import actionlib

from actionlib_msgs.msg import GoalStatus
from assistance_msgs.msg import (RequestAssistanceAction,
                                 RequestAssistanceResult, InterventionEvent)

from assistance_arbitrator.intervention_monitor import InterventionMonitor


# The server performs local behaviours ro resume execution after contacting a
# remote human

class RemoteRecoveryServer(object):
    """
    Given a request for assistance, this class interfaces with the robot's
    remote monitoring UIs to deal with the error
    """

    DEFAULT_RVIZ_VIEW = os.path.join(
        os.path.dirname(os.getenv("CMAKE_PREFIX_PATH", "/home/banerjs/Workspaces/fetch/").split(':')[0]),
        "fetch.rviz"
    )

    def __init__(self):
        # Instantiate the action server to perform the recovery
        self._server = actionlib.SimpleActionServer(
            rospy.get_name(),
            RequestAssistanceAction,
            self.execute,
            auto_start=False
        )

        # The remote interface pointers
        self._rviz_process = None

    def start(self):
        # Start the action server and indicate that we are ready
        self._server.start()
        rospy.loginfo("Remote strategy node ready...")

    def execute(self, goal):
        """Execute the request for assistance"""
        result = self._server.get_default_result()
        result.stats.request_received = rospy.Time.now()

        rospy.loginfo("Remote: Serving Assistance Request for: {} (status - {})"
                      .format(goal.component, goal.component_status))
        goal.context = pickle.loads(goal.context)

        # Start an rviz process and wait until it is shut
        self._rviz_process = subprocess.Popen(
            ["rosrun", "rviz", "rviz", "-d", RemoteRecoveryServer.DEFAULT_RVIZ_VIEW]
        )
        self._rviz_process.wait()

        # For now, simply return a stop as the desired behaviour
        result.stats.request_acked = rospy.Time.now()
        result.resume_hint = RequestAssistanceResult.RESUME_NONE

        # Then return
        result.stats.request_complete = rospy.Time.now()
        self._server.set_succeeded(result)

    def stop(self):
        pass
