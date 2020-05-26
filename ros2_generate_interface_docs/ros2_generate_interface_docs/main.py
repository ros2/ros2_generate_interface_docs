#!/usr/bin/env python3

# Copyright 2020 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys

from ros2_generate_interface_docs import action_utils
from ros2_generate_interface_docs import msg_utils
from ros2_generate_interface_docs import srv_utils
from ros2_generate_interface_docs import utils

from rosidl_runtime_py import get_action_interfaces
from rosidl_runtime_py import get_message_interfaces
from rosidl_runtime_py import get_service_interfaces


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Generate interfaces public API documentation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--outputdir', type=str, default='api',
        help='Output directory')
    args = parser.parse_args(argv)

    output_dir = args.outputdir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    html_dir = os.path.join(output_dir, 'html')
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)

    msg_template = utils.load_tmpl('msg.template')

    message_interfaces = get_message_interfaces()
    for package_name in sorted(message_interfaces):
        package_d = os.path.join(html_dir, package_name)
        msg_d = os.path.join(package_d, 'msg')
        if not os.path.exists(msg_d):
            os.makedirs(msg_d)
        msg_utils.generate_msg_index(package_name, package_d, message_interfaces[package_name])
        for message_name in sorted(message_interfaces[package_name]):
            print(message_name)
            text = msg_utils.generate_msg_doc('%s/%s' % (package_name, message_name),
                                              msg_template,
                                              package_d + '/' + message_name + '.html')
            with open(package_d + '/' + message_name + '.html', 'w') as f:
                f.write(text)

    action_template = utils.load_tmpl('action.template')
    action_interfaces = get_action_interfaces()
    for package_name in sorted(action_interfaces):
        package_d = os.path.join(html_dir, package_name)
        action_d = os.path.join(package_d, 'action')
        if not os.path.exists(action_d):
            os.makedirs(action_d)
        action_utils.generate_action_index(package_name,
                                           package_d,
                                           action_interfaces[package_name])
        for action_name in sorted(action_interfaces[package_name]):
            print(action_name)
            text = action_utils.generate_action_doc('%s/%s' % (package_name, action_name),
                                                    action_template,
                                                    package_d + '/' + action_name + '.html')
            with open(package_d + '/' + action_name + '.html', 'w') as f:
                f.write(text)

    service_interfaces = get_service_interfaces()
    for package_name in sorted(service_interfaces):
        package_d = os.path.join(html_dir, package_name)
        srv_d = os.path.join(package_d, 'srv')
        if not os.path.exists(srv_d):
            os.makedirs(srv_d)
        srv_utils.generate_srv_index(package_name, package_d, service_interfaces[package_name])
        for srv_name in sorted(service_interfaces[package_name]):
            print(srv_name)
            text = srv_utils.generate_srv_doc('%s/%s' % (package_name, srv_name),
                                              msg_template,
                                              package_d + '/' + srv_name + '.html')
            with open(package_d + '/' + srv_name + '.html', 'w') as f:
                f.write(text)

    utils.copy_css_style(html_dir)


if __name__ == '__main__':
    sys.exit(main())
