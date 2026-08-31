#!/usr/bin/env python3

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

import rclpy

from ntrip_ros_base import NTRIPRosBase
from ntrip_client.ntrip_client import NTRIPClient

class NTRIPRos(NTRIPRosBase):
  def __init__(self):
    # Init the node and declare params
    super().__init__('ntrip_client')
    self.declare_parameters(
      namespace='',
      parameters=[
        ('host', '127.0.0.1'),
        ('port', 2101),
        ('mountpoint', 'mount'),
        ('ntrip_version', 'None'),
        ('authenticate', False),
        ('username', ''),
        ('password', ''),
        ('ssl', False),
        ('cert', 'None'),
        ('key', 'None'),
        ('ca_cert', 'None'),
        ('rtcm_timeout_seconds', NTRIPClient.DEFAULT_RTCM_TIMEOUT_SECONDS),
      ]
    )

    # Read some mandatory config
    host = self.get_parameter('host').value
    port = self.get_parameter('port').value
    mountpoint = self.get_parameter('mountpoint').value

    # Optionally get the ntrip version from the launch file
    ntrip_version = self.get_parameter('ntrip_version').value
    if ntrip_version == 'None':
      ntrip_version = None

    # If we were asked to authenticate, read the username and password
    username = None
    password = None
    if self.get_parameter('authenticate').value:
      username = self.get_parameter('username').value
      password = self.get_parameter('password').value
      if not username:
        self.get_logger().error('Requested to authenticate, but param "username" was not set')
        sys.exit(1)
      if not password:
        self.get_logger().error('Requested to authenticate, but param "password" was not set')
        sys.exit(1)

    # Initialize the client
    self._client = NTRIPClient(
      host=host,
      port=port,
      mountpoint=mountpoint,
      ntrip_version=ntrip_version,
      username=username,
      password=password,
      logerr=self.get_logger().error,
      logwarn=self.get_logger().warning,
      loginfo=self.get_logger().info,
      logdebug=self.get_logger().debug
    )

    # Get some SSL parameters for the NTRIP client
    self._client.ssl = self.get_parameter('ssl').value
    self._client.cert = self.get_parameter('cert').value
    self._client.key = self.get_parameter('key').value
    self._client.ca_cert = self.get_parameter('ca_cert').value
    if self._client.cert == 'None':
      self._client.cert = None
    if self._client.key == 'None':
      self._client.key = None
    if self._client.ca_cert == 'None':
      self._client.ca_cert = None

    # Get some timeout parameters for the NTRIP client
    self._client.nmea_parser.nmea_max_length = self._nmea_max_length
    self._client.nmea_parser.nmea_min_length = self._nmea_min_length
    self._client.reconnect_attempt_max = self._reconnect_attempt_max
    self._client.reconnect_attempt_wait_seconds = self._reconnect_attempt_wait_seconds
    self._client.rtcm_timeout_seconds = self.get_parameter('rtcm_timeout_seconds').value

import argparse

if __name__ == '__main__':
  # Handle --help / -h gracefully
  if '--help' in sys.argv or '-h' in sys.argv:
    parser = argparse.ArgumentParser(
      prog='ros2 run ntrip_client ntrip_ros.py',
      description='NTRIP client ROS 2 node. Connects to an NTRIP caster and publishes RTCM corrections to /rtcm.',
      epilog='Recommended usage:\n  ros2 launch ntrip_client ntrip_client_launch.py (auto-loads ntrip_client.env)',
      formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.print_help()
    print('\nROS 2 Parameters (pass via --ros-args -p <param>:=<value>):')
    print('  host (string)                  Caster host/IP (default: "127.0.0.1")')
    print('  port (int)                     Caster port (default: 2101)')
    print('  mountpoint (string)            Mountpoint stream name (default: "mount")')
    print('  ntrip_version (string)         NTRIP version, e.g. "2.0.0" or "None"')
    print('  authenticate (bool)            Whether authentication is required (default: False)')
    print('  username (string)              Username for caster authentication')
    print('  password (string)              Password for caster authentication')
    print('  ssl (bool)                     Whether to use SSL (default: False)')
    print('  rtcm_message_package (string)  Message package: "rtcm_msgs" (default) or "mavros_msgs"')
    print('  rtcm_timeout_seconds (int)     Timeout before reconnecting (default: 4)')
    sys.exit(0)

  # Start the node
  rclpy.init()
  node = NTRIPRos()
  if not node.run():
    sys.exit(1)
  try:
    # Spin until we are shut down
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  except BaseException as e:
    raise e
  finally:
    node.stop()
    
    # Shutdown the node and stop rclpy
    rclpy.shutdown()