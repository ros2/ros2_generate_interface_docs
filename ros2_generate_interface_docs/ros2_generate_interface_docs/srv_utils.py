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

from collections import OrderedDict
import os
import time
from typing import Any

from ros2_generate_interface_docs import utils

from rosidl_parser.definition import AbstractNestedType, BASIC_TYPES, NamespacedType

from rosidl_runtime_py import get_interface_path
from rosidl_runtime_py.import_message import import_message_from_namespaced_type

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


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

    feedback_namespaced_type = NamespacedType([package, 'srv'], type_)
    imported_srv = import_message_from_namespaced_type(feedback_namespaced_type)

    # include constants
    ignored_keys = ['__slots__', '__doc__', '_fields_and_field_types', 'SLOT_TYPES', '__init__',
                    '__repr__', '__eq__', '__hash__', 'get_fields_and_field_types', '__module__']
    for imported_service in [imported_srv.Request, imported_srv.Response]:
        ignored_keys += list(imported_service.get_fields_and_field_types().keys())
        ignored_keys += ['_' + x for x in imported_service.get_fields_and_field_types().keys()]
        for key in imported_service.__dict__.keys():
            if key not in ignored_keys:
                buff.write('%s %s=%s<br />' % ('&nbsp;' * indent,
                                               key,
                                               getattr(imported_service, key)))

        # include fields
        message_fields = imported_service.get_fields_and_field_types()
        for field in message_fields.keys():
            if(message_fields[field] not in BASIC_TYPES and
               'string' not in message_fields[field]):
                slot_type = get_service_slot_types(imported_service)[field]
                if(isinstance(slot_type, AbstractNestedType)):
                    if(isinstance(slot_type.value_type, NamespacedType)):
                        pkg_name, in_type, msg_name = map(str,
                                                          slot_type.value_type.namespaced_name())
                        buff.write('%s%s %s<br />' % ('&nbsp;' * indent,
                                                      utils._href('../../' + pkg_name + '/msg/'
                                                                  + msg_name + '.html',
                                                                  '/'.join(slot_type.value_type.
                                                                           namespaced_name())),
                                                      field))
                else:
                    pkg_name, msg_name = message_fields[field].split('/')
                    href = '../../' + pkg_name + '/msg/' + msg_name + '.html'
                    buff.write('%s%s %s<br />' % ('nbsp;' * indent,
                                                  utils._href(href, message_fields[field]),
                                                  msg_name))
            else:
                buff.write('%s%s %s<br />' % ('&nbsp;' * indent, message_fields[field], field))
        if(imported_srv.Request == imported_service):
            buff.write('<hr/>')
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


def generate_srv_index(package, file_d, srvs):
    d = {'package': package, 'msg_list': '', 'srv_list': '',
         'action_list': '',
         'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}
    if srvs:
        d['srv_list'] = """<h2>Action types</h2>
<div class="msg-list">
  <ul>
%s
  </ul>
</div>""" % '\n'.join([' <li>%s</li>' % utils._href('../../html/' + package + '/' + m + '.html', m)
                       for m in srvs])
    msg_index_template = utils.load_tmpl('msg-index.template')
    file_p = os.path.join(file_d, 'index-msg.html')
    text = msg_index_template % d
    with open(file_p, 'w') as f:
        f.write(text)
