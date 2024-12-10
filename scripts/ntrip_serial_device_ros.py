#!/usr/bin/env python

import os
import sys
import json

import rclpy

from ntrip_ros_base import NTRIPRosBase
from ntrip_client.ntrip_serial_device import NTRIPSerialDevice

class NTRIPSerialDeviceRos(NTRIPRosBase):
  def __init__(self):
    # Init the node and declare params
    super().__init__('ntrip_serial_device')
    self.declare_parameters(
      namespace='',
      parameters=[
        ('port', '/dev/ttyACM0'),
        ('baudrate', 115200),
      ]
    )

    # Read some mandatory config
    port = self.get_parameter('port').value
    baudrate = self.get_parameter('baudrate').value

    # Initialize the client
    self._client = NTRIPSerialDevice(
      port=port,
      baudrate=baudrate,
      logerr=self.get_logger().error,
      logwarn=self.get_logger().warning,
      loginfo=self.get_logger().info,
      logdebug=self.get_logger().debug
    )

if __name__ == '__main__':
  # Start the node
  rclpy.init()
  node = NTRIPSerialDeviceRos()
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