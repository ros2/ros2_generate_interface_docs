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

import os

from ros2_generate_interface_docs import utils

from rosidl_parser.definition import NamespacedType

from rosidl_runtime_py import get_message_slot_types
from rosidl_runtime_py.import_message import import_message_from_namespaced_type


def generate_msg_text_from_spec(package, interface_name, indent=0):
    """
    Generate a dictionary with the compact message.

    Compact message contains:
        - Constants
        - messge fields. If the message contains other composed interfaces
          a link will be added to this interfaces.

    Parameters
    ----------
    package: str
        name of the package
    interface_name: str
        name of the message
    indent: int, optional
        number of indentations to add to the generated text

    Returns
    -------
    dictionary with the compact definition (constanst and message with links)

    """
    namespaced_type = NamespacedType([package, 'msg'], interface_name)
    imported_message = import_message_from_namespaced_type(namespaced_type)
    return utils.generate_compact_definition(imported_message,
                                             indent,
                                             get_message_slot_types)
