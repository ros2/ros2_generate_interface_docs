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
import time

from ros2_generate_interface_docs import msg_utils
from ros2_generate_interface_docs import utils

from rosidl_runtime_py import get_message_interfaces


def generate_interfaces(interfaces, html_dir, template, interface_type):
    """
    Generate the index and documentation for each message.

    :param interfaces: dictionary with the interface package name associated with all
        the interfaces for this package.
    :type interfaces: dict of {str : str[]}
    :param html_dir: path to the directory to save the generated documentation
    :type html_dir: str
    :param template_dir: template name
    :type template_dir: str
    :param interface_type: type of the interface: msg, action or srv
    :type interface_type: str
    """
    timestamp = time.gmtime()
    for package_name, interface_names in interfaces.items():
        package_directory = os.path.join(html_dir, package_name)
        interface_type_directory = os.path.join(package_directory, interface_type)
        os.makedirs(interface_type_directory, exist_ok=True)
        utils.generate_index(package_name, package_directory, interfaces[package_name], timestamp)
        for interface_name in interface_names:
            documentation_data = {
                'interface_name': interface_name,
                'interface_package': package_name,
                'timestamp': timestamp
            }

            if interface_type == 'msg':
                documentation_data = {
                    **documentation_data,
                    **{'ext': 'msg', 'type': 'Message'}
                }
                function_to_generate_text_from_spec = msg_utils.generate_msg_text_from_spec

            utils.generate_interface_documentation(
                '%s/%s' % (package_name, interface_name),
                template,
                os.path.join(package_directory, interface_name + '.html'),
                documentation_data,
                function_to_generate_text_from_spec)


def main(argv=sys.argv[1:]):
    """Parse the arguments and call the right logic."""
    parser = argparse.ArgumentParser(
        description='Generate interfaces public API documentation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--outputdir', type=str, default='api',
        help='Output directory')
    args = parser.parse_args(argv)

    html_dir = os.path.join(args.outputdir, 'html')
    os.makedirs(html_dir, exist_ok=True)

    # generate msg interfaces
    generate_interfaces(get_message_interfaces(), html_dir, 'msg.html.em', 'msg')

    utils.copy_css_style(html_dir)


if __name__ == '__main__':
    sys.exit(main())
