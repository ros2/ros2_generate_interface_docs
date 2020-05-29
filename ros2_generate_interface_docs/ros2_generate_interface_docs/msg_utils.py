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

from io import StringIO
import os
import time

from ros2_generate_interface_docs import utils

from rosidl_parser.definition import NamespacedType

from rosidl_runtime_py import get_interface_path
from rosidl_runtime_py import get_message_slot_types
from rosidl_runtime_py.import_message import import_message_from_namespaced_type


message_list_str = """<h2>Message types</h2><div class="msg-list"> <ul> %s </ul> </div>"""


def _generate_msg_text_from_spec(package, type_, spec, buff=None, indent=0):
    if buff is None:
        buff = StringIO()

    namespaced_type = NamespacedType([package, 'msg'], type_)
    imported_message = import_message_from_namespaced_type(namespaced_type)

    buff = utils.generate_fancy_doc(imported_message, buff, indent, get_message_slot_types, False)

    return buff.getvalue()


def generate_msg_doc(msg, msg_template, path):
    package, interface, base_type = utils.resource_name(msg)
    d = {'name': msg, 'ext': 'msg', 'type': 'Message',
         'package': package, 'base_type': base_type,
         'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}
    file_path = get_interface_path(msg)
    with open(file_path, 'r', encoding='utf-8') as h:
        spec = h.read().rstrip()

    d['fancy_text'] = _generate_msg_text_from_spec(package, base_type, spec)
    d['raw_text'] = utils.generate_raw_text(spec)
    return msg_template % d


def generate_msg_index(package, file_directory, msgs):
    package_message_dic = utils._TEMPLATE_DIC
    package_message_dic['package'] = package
    package_message_dic['date'] = str(time.strftime('%a, %d %b %Y %H:%M:%S'))
    if msgs:
        package_message_dic['msg_list'] = message_list_str % '\n'.join(
            [' <li>%s</li>' % utils._href('../../html/' + package + '/' + msg + '.html', msg)
             for msg in msgs])
    msg_index_template = utils.load_template('msg-index.template')
    file_p = os.path.join(file_directory, 'index-msg.html')
    text = msg_index_template % package_message_dic
    with open(file_p, 'w') as f:
        f.write(text)
