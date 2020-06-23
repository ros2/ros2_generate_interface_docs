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

import pathlib

from ament_index_python.packages import get_package_share_directory

from ros2_generate_interface_docs import utils

from rosidl_parser.definition import Action
from rosidl_parser.definition import IdlLocator
from rosidl_parser.parser import parse_idl_file


def generate_msg_text_from_spec(package, interface_name, indent=0):
    """
    Generate a dictionary with the compact message.

    Compact message contains:
        - Constants
        - messge fields. If the message contains other composed interfaces
          a link will be added to this interfaces.

    :param package: name of the package
    :type package: str:
    :param interface_name: name of the message
    :type interface_name: str
    :param indent: number of indentations to add to the generated text (default = 0)
    :type indent: int, optional
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    interface_location = IdlLocator(
        pathlib.Path(get_package_share_directory(package)),
        pathlib.Path('action') / (interface_name + '.idl')
    )
    message = parse_idl_file(interface_location).content.get_elements_of_type(Action)

    compact_srv = {}

    for attribute in ['goal', 'result', 'feedback']:
        definition = utils.generate_compact_definition(getattr(message[0], attribute), indent)
        utils.copy_dict_with_suffix(compact_srv, definition, attribute)

    return compact_srv
