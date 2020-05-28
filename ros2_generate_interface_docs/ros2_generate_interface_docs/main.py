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


# generic function takes op and its argument
def generate_interfaces(generate_index, generate_doc, interfaces,
                        html_dir, template, interface_type):
    for package_name, names in sorted(interfaces.items(), key=lambda item: item[0]):
        package_directory = os.path.join(html_dir, package_name)
        interface_type_directory = os.path.join(package_directory, interface_type)
        os.makedirs(interface_type_directory, exist_ok=True)
        generate_index(package_name,
                       package_directory,
                       interfaces[package_name])
        for name in names:
            text = generate_doc('%s/%s' % (package_name, name),
                                template,
                                os.path.join(package_directory, name + '.html'))
            with open(os.path.join(package_directory, name + '.html'), 'w') as f:
                f.write(text)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Generate interfaces public API documentation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--outputdir', type=str, default='api',
        help='Output directory')
    args = parser.parse_args(argv)

    output_dir = args.outputdir
    os.makedirs(output_dir, exist_ok=True)
    html_dir = os.path.join(output_dir, 'html')
    os.makedirs(html_dir, exist_ok=True)

    msg_template = utils.load_template('msg.template')
    action_template = utils.load_template('action.template')

    # generate msg interfaces
    generate_interfaces(msg_utils.generate_msg_index,
                        msg_utils.generate_msg_doc,
                        get_message_interfaces(),
                        html_dir,
                        msg_template,
                        'msg')

    # generate srv interfaces
    generate_interfaces(srv_utils.generate_srv_index,
                        srv_utils.generate_srv_doc,
                        get_service_interfaces(),
                        html_dir,
                        msg_template,
                        'srv')

    # generate action interfaces
    generate_interfaces(action_utils.generate_action_index,
                        action_utils.generate_action_doc,
                        get_action_interfaces(),
                        html_dir,
                        action_template,
                        'action')

    utils.copy_css_style(html_dir)


if __name__ == '__main__':
    sys.exit(main())
