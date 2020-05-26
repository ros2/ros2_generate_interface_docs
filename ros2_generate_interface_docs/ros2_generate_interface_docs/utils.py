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
import sys

_TEMPLATES_DIR = 'templates'


def _href(link, text):
    return '<a href="%(link)s">%(text)s</a>' % locals()


def generate_raw_text(raw_text):
    s = ''
    for line in raw_text.split('\n'):
        line = line.replace(' ', '&nbsp;')
        parts = line.split('#')
        if len(parts) > 1:
            s = s + parts[0] + '<font color="blue">#%s</font><br/>' % ('#'.join(parts[1:]))
        else:
            s = s + '%s<br/>' % parts[0]
    return s


def resource_name(resource):
    """Return the resource name."""
    if '/' in resource:
        val = tuple(resource.split('/'))
        if len(val) != 3:
            raise ValueError('invalid name [%s]' % resource)
        else:
            return val
    else:
        return '', '', resource


def get_templates_dir():
    """Return template directory."""
    return os.path.join(os.path.dirname(__file__), _TEMPLATES_DIR)


def copy_css_style(folder_name):
    """Copy the css style file in the folder_name."""
    style_css = load_tmpl('styles.css')
    with open(folder_name + '/styles.css', 'w') as f:
        f.write(style_css)

    msg_style_css = load_tmpl('msg-styles.css')
    with open(folder_name + '/msg-styles.css', 'w') as f:
        f.write(msg_style_css)


def load_tmpl(filename):
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
            sys.stderr.write("Template file '%s' is empty\n" % (filename))
            sys.exit(1)
        return content
