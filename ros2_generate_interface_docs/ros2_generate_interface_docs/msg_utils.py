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
import time

from ros2_generate_interface_docs import utils

from rosidl_parser.definition import NamespacedType

from rosidl_runtime_py import get_interface_path
from rosidl_runtime_py import get_message_slot_types
from rosidl_runtime_py.import_message import import_message_from_namespaced_type


def _generate_msg_text_from_spec(package, type_, spec, indent=0):
    namespaced_type = NamespacedType([package, 'msg'], type_)
    imported_message = import_message_from_namespaced_type(namespaced_type)
    return utils.generate_compact_definition(imported_message,
                                             indent,
                                             get_message_slot_types)


def generate_msg_doc(msg, msg_template, file_output_path):
    package, interface, base_type = utils.resource_name(msg)
    msg_doc_dic = {'name': msg,
                   'ext': 'msg',
                   'type': 'Message',
                   'package': package,
                   'base_type': base_type,
                   'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}

    file_path = get_interface_path(msg)
    with open(file_path, 'r', encoding='utf-8') as h:
        spec = h.read().rstrip()

    compact_definition = _generate_msg_text_from_spec(package, base_type, spec)
    msg_doc_dic['raw_text'] = utils.generate_raw_text(spec)
    utils.write_template('msg.html.em', {**msg_doc_dic, **compact_definition}, file_output_path)


def generate_msg_index(package, file_directory, msgs):
    package_message_dic = {}
    package_message_dic['package'] = package
    package_message_dic['date'] = str(time.strftime('%a, %d %b %Y %H:%M:%S'))
    if msgs:
        package_message_dic['links'] = [package + '/' + msg + '.html' for msg in msgs]
        package_message_dic['interface_list'] = msgs
    file_output_path = os.path.join(file_directory, 'index-msg.html')
    utils.write_template('msg-index.html.em', package_message_dic, file_output_path)
