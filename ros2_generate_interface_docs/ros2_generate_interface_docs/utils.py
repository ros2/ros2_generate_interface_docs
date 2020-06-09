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

import array
import errno
import html
from io import StringIO
import os
import sys

import em

from rosidl_parser.definition import AbstractNestedType, BoundedSequence, NamespacedType

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

    :returns: the directory of the template directory
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


BASIC_TYPE_CONVERSION = {
    'boolean': 'bool',
    'octet': 'bytes',
    'uint8': 'uint8',
    'int8': 'int8',
    'uint16': 'uint16',
    'int16': 'int16',
    'uint32': 'uint32',
    'int32': 'int32',
    'uint64': 'uint64',
    'int64': 'int64',
    'char': 'str',
    'float': 'float32',
    'double': 'float64',
    'short': 'int',
    'unsigned short': 'int',
    'long': 'int',
    'unsigned long': 'int',
    'long long': 'int',
    'unsigned long long': 'int',
    'string': 'string',
    'wstring': 'wstring'
}


def fill_namespaced_type(compact, field, field_type, size_sequence_str, default_str, value_type):
    """
    Fill compact structure with a namespaced type.

    :param compact: dictionary with the compact definition (constanst and message with links)
    :type compact: dict
    :param field: name of the field in the interface
    :type field: str
    :param field_type: type of the field in the interface
    :type field_type: str
    :param size_sequence_str: string with the size of the field. (for example, '', [2], [], [<=3])
    :type size_sequence_str: str
    :param value_type: define the type of the field inside Python
    :type value_type: rosidl_parser.definition.NamespacedType
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    pkg_name, in_type, msg_name = map(str,
                                      value_type.namespaced_name())
    compact['links'].append(pkg_name + '/msg/' + msg_name + '.html')
    if '[' in field_type:
        compact['field_types'].append(field_type + size_sequence_str)
    else:
        compact['field_types'].append(
            '/'.join(value_type.namespaced_name()) + size_sequence_str)
    compact['field_names'].append(field + default_str)
    return compact


def fill_basic_type(compact, field, field_type, size_sequence_str, default_str):
    """
    Fill compact structure with a basic type.

    :param compact: dictionary with the compact definition (constanst and message with links)
    :type compact: dict
    :param field: name of the field in the interface
    :type field: str
    :param field_type: type of the field in the interface
    :type field_type: str
    :param size_sequence_str: string with the size of the field. (for example, '', [2], [], [<=3])
    :type size_sequence_str: str
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    if 'string<' not in field_type and '[' not in field_type:
        compact['field_types'].append(
            BASIC_TYPE_CONVERSION[field_type] + size_sequence_str)
    else:
        if 'string<' in field_type:
            compact['field_types'].append(
                field_type.split('<')[0] + '<=' + field_type.split('<')[1][:-1])
        else:
            compact['field_types'].append(field_type + size_sequence_str)

    compact['links'].append('')
    compact['field_names'].append(field + default_str)
    return compact


def handle_constants_and_default_values(imported_interface):
    """
    Fill the compact structure with constant and return default values.

    :param imported_interface: class with all the data about the interface
    :type imported_interface: interface class
    :returns: dictionary with the compact definition (constanst and message with links) and a list
        with the default value names
    :rtype: dict, list
    """
    ignored_keys_ = IGNORED_KEYS
    ignored_keys_ += list(imported_interface.get_fields_and_field_types().keys())
    ignored_keys_ += ['_'+x for x in imported_interface.get_fields_and_field_types().keys()]
    compact = {'constant_types': [],
               'constant_names': [],
               'links': [],
               'field_types': [],
               'field_names': []}
    fields_with_default_value = []
    for key in imported_interface.__dict__.keys():
        if key not in ignored_keys_ and '__DEFAULT' not in key:
            compact['constant_types'].append(key)
            compact['constant_names'].append(getattr(imported_interface, key))
        if '__DEFAULT' in key:
            fields_with_default_value.append(key.replace('__DEFAULT', '').lower())
    return compact, fields_with_default_value


def get_default_value(imported_interface, field, fields_with_default_value):
    """
    Get the default value from a field if exists otherwise return an empty string.

    :param imported_interface: class with all the data about the interface
    :type imported_interface: interface class
    :param field: name of the field in the interface
    :type field: str
    :param fields_with_default_value:list with the default value names
    :type fields_with_default_value: list
    :returns: default value from a field if exists otherwise return an empty string
    :rtype: str
    """
    default_str = ''
    if field in fields_with_default_value:
        default_value = imported_interface.__dict__[field.upper() + '__DEFAULT']
        default_str = '=' + str(default_value)
        if isinstance(default_value, array.array):
            default_str = '=' + str(default_value.tolist())
        else:
            default_str = '=' + str(default_value)
    return default_str


def get_type_and_size_from_sequence(compact, field, field_type, default_value_str, slot_type):
    """
    Get the type and size from a sequence.

    :param compact: dictionary with the compact definition (constanst and message with links)
    :type compact: dict
    :param field: name of the field in the interface
    :type field: str
    :param field_type: type of the field in the interface
    :type field_type: str
    :param default_value_str: default value
    :type default_value_str: str
    :param slot_type: type of sequence
    :type slot_type: rosidl_parser.definition(UnboundedSequence, BoundedString, BoundedSequence)
    :returns: dictionary with the compact definition (constanst and message with links),
        string with the type of the secuence and a string with the size of the sequence
    :rtype: dict, str, str
    """
    field_type_compact = field_type
    type_sequence = field_type.split('<')[1][:-1]
    compact['field_names'].append(field + default_value_str)
    type_sequence_with_size = type_sequence.split(',')
    size_sequence_str = '[]'
    if 'string<' not in field_type:
        field_type_compact = type_sequence
    if len(type_sequence_with_size) > 1:
        if isinstance(slot_type, BoundedSequence):
            size_sequence_str = '[<=' + type_sequence_with_size[1] + ']'
        else:
            size_sequence_str = '[' + type_sequence_with_size[1] + ']'
        field_type_compact = type_sequence_with_size[0]
    return compact, field_type_compact, size_sequence_str


def generate_compact_definition(imported_interface, indent, get_slot_types):
    """
    Create the compact definition dictionary.

    This function removes all the common dictionary keys to get all the constants in the message
    dictionary. Then it will generate a dictionary with the constants and field of the message.
    If the field type is a message interface itself, then this text will contain a link to this
    interface.

    :param imported_interface: class with all the data about the interface
    :type imported_interface:
    :param indent: number of indentations to add to the generated text
    :type indent: int
    :param get_slot_types: function that returns an OrderedDict of the slot types of a message.
    :type get_slot_types: function
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    compact, fields_with_default_value = handle_constants_and_default_values(imported_interface)

    fields = imported_interface.get_fields_and_field_types()

    for field, field_type in fields.items():
        # check if there are some default values
        default_value_str = get_default_value(imported_interface, field, fields_with_default_value)

        slot_type = get_slot_types(imported_interface)[field]

        size_sequence_str = ''
        field_type_compact = field_type
        if 'sequence' in field_type or 'string<' in field_type:
            compact, field_type_compact, size_sequence_str = get_type_and_size_from_sequence(
                compact, field, field_type, default_value_str, slot_type)

        if(isinstance(slot_type, AbstractNestedType)):
            if(isinstance(slot_type.value_type, NamespacedType)):
                compact = fill_namespaced_type(
                    compact, field, field_type_compact,
                    size_sequence_str, default_value_str, slot_type.value_type)
            else:
                compact = fill_basic_type(
                    compact, field, field_type_compact,
                    size_sequence_str, default_value_str)
        else:
            field_type_tokens = field_type_compact.split('/')
            if len(field_type_tokens) > 1:
                compact = fill_namespaced_type(
                    compact, field, field_type_compact,
                    size_sequence_str, default_value_str, slot_type)
            else:
                compact = fill_basic_type(
                    compact, field, field_type_compact,
                    size_sequence_str, default_value_str)

    return compact
