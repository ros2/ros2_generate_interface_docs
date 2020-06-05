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

import errno
import html
from io import StringIO
import os
import sys

import em

from rosidl_parser.definition import AbstractNestedType, BASIC_TYPES, NamespacedType

from rosidl_runtime_py import get_interface_path


_TEMPLATES_DIR = 'templates'
IGNORED_KEYS = ['__slots__', '__doc__', '_fields_and_field_types', 'SLOT_TYPES', '__init__',
                '__repr__', '__eq__', '__hash__', 'get_fields_and_field_types', '__module__']


def generate_raw_text(raw_text):
    """
    Generate the text HTML for the message fields.

    Lines that starts with '#' (comments) will be shown in blue, otherwise black.

    :param raw_text: content of the interface
    :type raw_text: str
    :returns: string with the generated HTML
    :rtype: str
    """
    raw_str = ''
    for line in raw_text.splitlines():
        parts = line.split('#')
        if len(parts) > 1:
            raw_str = raw_str + parts[0] \
                + '<a style="color:blue">#%s</a></br>\n' % ('#'.join(parts[1:]))
        else:
            raw_str = raw_str + '%s<br/>\n' % parts[0]
    return html.escape(raw_str)


def resource_name(resource):
    """
    Return the resource name.

    :param resource: resource name of the interface
    :type resource: str
    :returns: a tuple with the 3 part of the resource name (for example: std_msgs/msg/Bool ->
        ('std_msgs', 'msg', 'Bool'))
    :rtype: tuple
    """
    if '/' not in resource:
        return '', '', resource
    values = resource.split('/')
    if len(values) != 3:
        raise ValueError('Resource name "{}" is malformed'.format(resource))
    return tuple(values)


def get_templates_dir():
    """
    Return template directory.

    :returns: return the directory of the template directory
    :rtype: str
    """
    return os.path.join(os.path.dirname(__file__), _TEMPLATES_DIR)


def copy_css_style(folder_name):
    """
    Copy the css style files in the folder_name.

    :param folder_name: name of the folder where the style css files will be copied
    :type folder_name: str
    """
    for style in ['styles.css', 'msg-styles.css']:
        style_css, _ = load_template(style)
        with open(os.path.join(folder_name, style), 'w') as f:
            f.write(style_css)


def load_template(input_filename):
    """
    Look up file within rosdoc ROS package.

    return its content, may sys.exit on error.
    Contents are cached with filename as key.

    :param input_filename: name of the template to be loaded
    :type input_filename: str
    :returns: cached file contents and filename of the template concat with
        the template directory
    :rtype: tuple
    """
    filename = os.path.join(get_templates_dir(), input_filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), filename)
    with open(filename, 'r') as f:
        content = f.read()
        if not content:
            raise Exception("Template file '%s' is empty\n" % (filename))
        return content, filename


def generate_interface_documentation(interface, interface_template, file_output_path,
                                     documentation_data, generate_text_from_spec):
    """
    Generate documentation for a single ROSIDL interface.

    This function write in a file the message static HTML site.

    :param interface: name of the interface
    :type interface: str
    :param interface_template: name of the template
    :type interface_template: str
    :param file_output_path: name of the file where the template will be written
        once filled
    :type file_output_path: str
    :param documentation_data: dictionary with the data to field the index template
    :type documentation_data: dict
    :param generate_text_from_spec: function with the logic to fill the compact
        definition for a specific type of interface
    :type generate_text_from_spec: function
    """
    package, interface_type, base_type = resource_name(interface)
    file_path = get_interface_path(interface)
    with open(file_path, 'r', encoding='utf-8') as h:
        spec = h.read().rstrip()

    compact_definition = generate_text_from_spec(package, base_type, spec)
    documentation_data['raw_text'] = generate_raw_text(spec)
    content = evaluate_template(interface_template,
                                {**documentation_data, **compact_definition})
    write_template(content, file_output_path)


def generate_index(package, file_directory, interfaces, timestamp):
    """
    Generate the message index page.

    :param package: package name
    :type package: str
    :param file_directory: directory where the index site will be located
    :type file_directory: str
    :param interfaces: list the the interfaces associated with the package
    :type interfaces: str
    :param timestamp: time to be included in all the generated files
    :type timestamp: time
    """
    package_index_data = {}
    package_index_data['package'] = package
    package_index_data['date'] = timestamp
    if interfaces:
        package_index_data['links'] = [package + '/' + msg + '.html' for msg in interfaces]
        package_index_data['interface_list'] = interfaces
    file_output_path = os.path.join(file_directory, 'index-msg.html')
    content = evaluate_template('msg-index.html.em', package_index_data)
    write_template(content, file_output_path)


def write_template(content, output_file):
    """
    Write the data in the template.

    :param content: data to write in the file
    :type content: str
    :param output_file: path where the file will be written
    :type output_file: str
    """
    with open(os.path.join(output_file), 'w') as f:
        f.write(content)


def evaluate_template(template_name, data):
    """
    Write the data in the template.

    :param template_dir: name of the template to write
    :type template_dir: str
    :param data: data that is used to fill the template
    :type template_dir: dict
    :returns: string with the template evaluated
    :rtype: str
    """
    msg_index_template, template_path = load_template(template_name)
    output = StringIO()
    interpreter = em.Interpreter(
        output=output,
        options={
            em.BUFFERED_OPT: True,
            em.RAW_OPT: True,
        },
    )
    try:
        with open(template_path, 'r') as h:
            template_content = h.read()
            interpreter.invoke(
                'beforeFile', name=template_name, file=h, locals=data)
        interpreter.string(template_content, template_path, locals=data)
        interpreter.invoke('afterFile')
    except Exception as e:  # noqa: F841
        print(f"{e.__class__.__name__} when expanding '{template_name}' "
              f": '{e}'", file=sys.stderr)
        raise

    content = output.getvalue()
    interpreter.shutdown()

    return content


def generate_compact_definition(imported_interface, indent, get_slot_types):
    """
    Create the compact definition dictionary.

    This function remove all the common dict keys to get all the contants in the message
    dictionary. Then it will generate a dictionary will the contants and field of the message.
    If the message is based in other message, then this text will contain a link to this
    interface.

    :param imported_interface: class with all the data about the interface
    :type imported_interface:
    :param indent: number of indentations to add to the generated text
    :type indent: int
    :param get_slot_types: function that returns an OrderedDict of the slot types of a message.
    :type get_slot_types: function
    :returns: Dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    ignored_keys_ = IGNORED_KEYS
    ignored_keys_ += list(imported_interface.get_fields_and_field_types().keys())
    ignored_keys_ += ['_'+x for x in imported_interface.get_fields_and_field_types().keys()]
    compact = {'constant_types': [],
               'constant_names': [],
               'links': [],
               'field_types': [],
               'field_names': []}
    for key in imported_interface.__dict__.keys():
        if key not in ignored_keys_:
            compact['constant_types'].append(key)
            compact['constant_names'].append(getattr(imported_interface, key))

    fields = imported_interface.get_fields_and_field_types()
    for field, field_types in fields.items():
        if(
            field_types not in BASIC_TYPES and
           'string' not in field_types
           ):
            slot_type = get_slot_types(imported_interface)[field]
            if(isinstance(slot_type, AbstractNestedType)):
                if(isinstance(slot_type.value_type, NamespacedType)):
                    pkg_name, in_type, msg_name = map(str,
                                                      slot_type.value_type.namespaced_name())
                    compact['links'].append(pkg_name + '/msg/' + msg_name + '.html')
                    compact['field_types'].append('/'.join(slot_type.value_type.namespaced_name()))
                    compact['field_names'].append(field)
            else:
                pkg_name, msg_name = field_types.split('/')
                compact['links'].append(pkg_name + '/msg/' + msg_name + '.html')
                compact['field_types'].append(field_types)
                compact['field_names'].append(msg_name)
        else:
            compact['links'].append('')
            compact['field_types'].append(field_types)
            compact['field_names'].append(field)
    return compact
