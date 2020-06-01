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

    Parameters
    ----------
    interfaces: dict of {str : str[]}
        dictionary with the interface package name associated with all the interface
        for this package.
    html_dir: str
        path to the directory to save the generated documentation
    template: str
        template name
    interface_type: str
        type of the interface: msg, action or srv

    """
    for package_name, names in sorted(interfaces.items(), key=lambda item: item[0]):
        package_directory = os.path.join(html_dir, package_name)
        interface_type_directory = os.path.join(package_directory, interface_type)
        os.makedirs(interface_type_directory, exist_ok=True)
        utils.generate_index(package_name,
                             package_directory,
                             interfaces[package_name])
        for name in names:
            doc_dic = {'name': name,
                       'package': package_name,
                       'base_type': name,
                       'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}

            if(interface_type == 'msg'):
                doc_dic = {**doc_dic, **{'ext': 'msg', 'type': 'Message'}}
                function_to_generate_text_from_spec = msg_utils.generate_msg_text_from_spec

            utils.generate_doc('%s/%s' % (package_name, name),
                               template,
                               os.path.join(package_directory, name + '.html'),
                               doc_dic,
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

    output_dir = args.outputdir
    os.makedirs(output_dir, exist_ok=True)
    html_dir = os.path.join(output_dir, 'html')
    os.makedirs(html_dir, exist_ok=True)

    # generate msg interfaces
    generate_interfaces(get_message_interfaces(),
                        html_dir,
                        'msg.html.em',
                        'msg')

    utils.copy_css_style(html_dir)


if __name__ == '__main__':
    sys.exit(main())
