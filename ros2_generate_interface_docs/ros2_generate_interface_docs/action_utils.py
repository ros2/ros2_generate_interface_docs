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

from ros2_generate_interface_docs import utils

from rosidl_runtime_py import get_interface_path


def generate_action_doc(action, action_template, path):
    package, interface, base_type = utils.resource_name(action)
    d = {'name': action, 'ext': 'action', 'type': 'Action',
         'package': package, 'base_type': base_type,
         'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}
    file_path = get_interface_path(action)
    with open(file_path, 'r', encoding='utf-8') as h:
        raw_text = h.read().rstrip()

    d['raw_text'] = utils.generate_raw_text(raw_text)
    return action_template % d


def generate_action_index(package, file_d, actions):
    d = {'package': package, 'msg_list': '', 'srv_list': '',
         'action_list': '',
         'date': str(time.strftime('%a, %d %b %Y %H:%M:%S'))}
    if actions:
        d['action_list'] = """<h2>Action types</h2>
<div class="msg-list">
  <ul>
%s
  </ul>
</div>""" % '\n'.join([' <li>%s</li>' % utils._href('../../html/' + package + '/' + m + '.html', m)
                       for m in actions])
    msg_index_template = utils.load_tmpl('msg-index.template')
    file_p = os.path.join(file_d, 'index-msg.html')
    text = msg_index_template % d
    with open(file_p, 'w') as f:
        f.write(text)
