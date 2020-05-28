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

import os
import time
from collections import OrderedDict
from typing import Any

from ros2_generate_interface_docs import utils

from rosidl_parser.definition import NamespacedType

from rosidl_runtime_py import get_interface_path
from rosidl_runtime_py.import_message import import_message_from_namespaced_type

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


service_list_str = """<h2>Service types</h2><div class="msg-list"> <ul> %s </ul> </div>"""


def get_service_slot_types(srv: Any) -> OrderedDict:
    """
    Return an OrderedDict of the slot types of a message.

    :param msg: The ROS message to get members types from.
    :returns: An OrderedDict with message member names as keys and slot types as values.
    """
    return OrderedDict(zip([s[1:] for s in srv.__slots__], srv.SLOT_TYPES))


def _generate_srv_text_from_spec(package, type_, spec, buff=None, indent=0):
    if buff is None:
        buff = StringIO()

    namespaced_type = NamespacedType([package, 'srv'], type_)
    imported_srv = import_message_from_namespaced_type(namespaced_type)

    for imported_service in [imported_srv.Request, imported_srv.Response]:
        buff = utils.generate_fancy_doc(imported_service,
                                        buff,
                                        indent,
                                        get_service_slot_types,
                                        imported_service == imported_srv.Request)
    return buff.getvalue()


def generate_srv_doc(srv, msg_template, path):
    package, interface, base_type = utils.resource_name(srv)
    d = {'name': srv, 'ext': 'srv', 'type': 'Service',
         'package': package, 'base_type': base_type,
         'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}
    file_path = get_interface_path(srv)
    with open(file_path, 'r', encoding='utf-8') as h:
        raw_text = h.read().rstrip()

    d['fancy_text'] = _generate_srv_text_from_spec(package, base_type, raw_text)
    d['raw_text'] = utils.generate_raw_text(raw_text)
    return msg_template % d


def generate_srv_index(package, file_directory, srvs):
    package_service_dic = utils._TEMPLATE_DIC
    package_service_dic['package'] = package
    package_service_dic['date'] = str(time.strftime('%a, %d %b %Y %H:%M:%S'))
    if srvs:
        package_service_dic['srv_list'] = service_list_str % '\n'.join(
            [' <li>%s</li>' % utils._href('../../html/' + package + '/' + srv + '.html', srv)
             for srv in srvs])

    msg_index_template = utils.load_template('msg-index.template')
    file_p = os.path.join(file_directory, 'index-msg.html')
    text = msg_index_template % package_service_dic
    with open(file_p, 'w') as f:
        f.write(text)
