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
import sys

from rosidl_parser.definition import AbstractNestedType, BASIC_TYPES, NamespacedType

_TEMPLATES_DIR = 'templates'
_TEMPLATE_DIC = {'package': '',
                 'msg_list': '',
                 'srv_list': '',
                 'action_list': '',
                 'date': ''}
IGNORED_KEYS = ['__slots__', '__doc__', '_fields_and_field_types', 'SLOT_TYPES', '__init__',
                '__repr__', '__eq__', '__hash__', 'get_fields_and_field_types', '__module__']


def _href(link, text):
    return '<a href="%s">%s</a>' % (link, text)


def generate_raw_text(raw_text):
    raw_test_str = ''
    for line in raw_text.split(os.linesep):
        line = line.replace(' ', '&nbsp;')
        parts = line.split('#')
        if len(parts) > 1:
            raw_test_str = raw_test_str + parts[0] \
                + '<font color="blue">#%s</font><br/>' % ('#'.join(parts[1:]))
        else:
            raw_test_str = raw_test_str + '%s<br/>' % parts[0]
    return raw_test_str


def resource_name(resource):
    """Return the resource name."""
    if '/' not in resource:
        return '', '', resource
    values = resource.split('/')
    if len(values) != 3:
        raise ValueError(...)
    return tuple(values)


def get_templates_dir():
    """Return template directory."""
    return os.path.join(os.path.dirname(__file__), _TEMPLATES_DIR)


def copy_css_style(folder_name):
    """Copy the css style file in the folder_name."""
    style_css = load_template('styles.css')
    with open(os.path.join(folder_name, 'styles.css'), 'w') as f:
        f.write(style_css)

    msg_style_css = load_template('msg-styles.css')
    with open(os.path.join(folder_name, 'msg-styles.css'), 'w') as f:
        f.write(msg_style_css)


def load_template(filename):
    """
    Look up file within rosdoc ROS package.

    return its content, may sys.exit on error.
    Contents are cached with filename as key.

    :returns: cached file contents
    """
    filename = os.path.join(get_templates_dir(), filename)
    if not os.path.isfile(filename):
        sys.stderr.write("Cannot locate template file '%s'\n" % (filename))
        sys.exit(1)
    with open(filename, 'r') as f:
        content = f.read()
        if not content:
            raise Exception("Template file '%s' is empty\n" % (filename))
        return content


def generate_fancy_doc(imported_interface, buff, indent, get_slot_types, need_separator):
    ignored_keys_ = IGNORED_KEYS
    ignored_keys_ += list(imported_interface.get_fields_and_field_types().keys())
    ignored_keys_ += ['_'+x for x in imported_interface.get_fields_and_field_types().keys()]
    for key in imported_interface.__dict__.keys():
        if key not in ignored_keys_:
            buff.write('%s %s=%s<br/>' % ('&nbsp;' * indent,
                                          key,
                                          getattr(imported_interface, key)))
#
    fields = imported_interface.get_fields_and_field_types()
    for field in fields.keys():
        if(fields[field] not in BASIC_TYPES and
           'string' not in fields[field]):
            slot_type = get_slot_types(imported_interface)[field]
            if(isinstance(slot_type, AbstractNestedType)):
                if(isinstance(slot_type.value_type, NamespacedType)):
                    pkg_name, in_type, msg_name = map(str,
                                                      slot_type.value_type.namespaced_name())
                    href_str = _href('../../' + pkg_name + '/msg/' + msg_name + '.html',
                                     '/'.join(slot_type.value_type.namespaced_name()))
                    buff.write('%s%s %s<br />' % ('&nbsp;' * indent, href_str, field))
            else:
                pkg_name, msg_name = fields[field].split('/')
                href_str = _href('../../' + pkg_name + '/msg/' + msg_name + '.html', fields[field])
                buff.write('%s%s %s<br />' % ('&nbsp;' * indent, href_str, msg_name))
        else:
            buff.write('%s%s %s<br />' % ('&nbsp;' * indent, fields[field], field))
        if(need_separator):
            buff.write('<hr/>')
    return buff
