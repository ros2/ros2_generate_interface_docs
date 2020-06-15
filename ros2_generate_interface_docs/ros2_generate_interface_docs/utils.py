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
from io import StringIO
import os
import shutil
import sys

import em

from rosidl_parser.definition import (
    AbstractGenericString, AbstractString, Array, BasicType, BoundedSequence,
    BoundedString, NamespacedType, UnboundedSequence
)

from rosidl_runtime_py import get_interface_path

_TEMPLATES_DIR = 'templates'


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
        shutil.copy(os.path.join(get_templates_dir(), style), os.path.join(folder_name, style))


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
    documentation_data['raw_text'] = spec
    content = evaluate_template(
        interface_template,
        {**documentation_data, **compact_definition})
    write_template(content, file_output_path)


def generate_index(package, file_directory, interfaces, timestamp):
    """
    Generate the message index page.

    :param package: package name
    :type package: str
    :param file_directory: directory where the index site will be located
    :type file_directory: str
    :param interfaces: dictionary with msgs, srvs and action for the specific package name
    :type interfaces: dict
    :param timestamp: time to be included in all the generated files
    :type timestamp: time
    """
    package_index_data = {}
    package_index_data['package'] = package
    package_index_data['timestamp'] = timestamp

    for keys in interfaces:
        package_index_data[keys + '_relative_paths'] = [
            package + '/' + msg + '.html' for msg in interfaces[keys]]
        package_index_data[keys + '_list'] = interfaces[keys]

    file_output_path = os.path.join(file_directory, 'index.html')
    content = evaluate_template('index.html.em', package_index_data)
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


def copy_dict_with_prefix(compact_srv, compact, suffix):
    """
    Copy a dictionary addind a suffix in the keys.

    :param compact_srv: dictionary to set the value with the new key
    :type compact_srv: dict
    :param compact: dictionary to copy
    :type compact: dict
    :param suffix:
    :type suffix: str
    """
    for key in compact.keys():
        compact_srv[key + '_' + suffix] = compact[key]


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


def get_field_type_and_link(field):
    """
    Get the field type and link from a rosidl_parser.definition.Member.

    :param interface_field: field to get the field and the link if it's a NamespacedType
    :type interface_field: rosidl_parser.definition.Member
    :returns: a string with field type and the relative link to the NamespacedType
    :rtype: str, str
    """
    link = ''
    if(isinstance(field.type.value_type, AbstractGenericString)):
        type_field = 'string'
    elif(isinstance(field.type.value_type, NamespacedType)):
        type_field = '/'.join(field.type.value_type.namespaced_name())
        link = type_field + '.html'
    else:
        type_field = field.type.value_type.typename
    return type_field, link


def read_constants(imported_interface, compact):
    """
    Set constant in the compact structure.

    :param imported_interface: interface to read all the constants
    :type interface_field: rosidl_parser.definition.Message
    :param compact: dictionary with the compact definition
        (constanst and message with links)
    :type compact: dict
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    constants = imported_interface.constants
    for constant in constants:
        compact['constant_names'].append(constant.name + '=' + str(constant.value))
        if(isinstance(constant.type, BasicType)):
            compact['constant_types'].append(constant.type.typename)
        elif(isinstance(constant.type, AbstractGenericString)):
            compact['constant_types'].append('string')
    return compact


def read_default(field):
    """
    Read the default value otherwise return an empty string.

    :param field: field to get the default value if exists
    :type field: rosidl_parser.definition.Member
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    if(field.has_annotations('default')):
        return '=' + str(field.get_annotation_values('default')[0]['value'])
    else:
        return ''


def generate_compact_definition(imported_interface, indent):
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
    :returns: dictionary with the compact definition (constanst and message with links)
    :rtype: dict
    """
    compact = {
        'constant_types': [],
        'constant_names': [],
        'relative_paths': [],
        'field_types': [],
        'field_names': [],
        'field_default_values': []
    }

    compact = read_constants(imported_interface, compact)

    for field in imported_interface.structure.members:

        compact['field_default_values'].append(read_default(field))

        type_field = ''
        array_definition_str = ''
        link = ''
        if(isinstance(field.type, BasicType)):
            type_field = field.type.typename
        elif(isinstance(field.type, Array)):
            type_field, link = get_field_type_and_link(field)
            if(field.type.has_maximum_size()):
                array_definition_str = '[' + str(field.type.size) + ']'
            else:
                array_definition_str = '[]'
        elif(isinstance(field.type, AbstractGenericString)):
            type_field = 'string'
            if(isinstance(field.type, BoundedString)):
                type_field = 'string[&lt;=' + str(field.type.maximum_size) + ']'
        elif(isinstance(field.type, NamespacedType)):
            type_field = '/'.join(field.type.namespaced_name())
            link = type_field + '.html'
        elif(isinstance(field.type, UnboundedSequence)):
            array_definition_str = '[]'
            type_field, link = get_field_type_and_link(field)
        elif(isinstance(field.type, BoundedSequence)):
            array_definition_str = '[&lt;=' + str(field.type.maximum_size) + ']'
            type_field, link = get_field_type_and_link(field)
        elif(isinstance(field.type.value_type, Array)):
            if(field.type.value_type.has_maximum_size()):
                array_definition_str = '[]'
            else:
                array_definition_str = '[' + field.type.value_type.maximum_size + ']'
        elif(isinstance(field.type.value_type, AbstractString)):
            type_field = 'string'
            if(isinstance(field.type, BoundedString)):
                type_field = 'string[&lt;=' + str(field.type.maximum_size) + ']'
        elif(isinstance(field.type.value_type, NamespacedType)):
            type_field = '/'.join(field.type.value_type.namespaced_name())
            link = type_field + '.html'
        else:
            type_field = str(field.type.value_type.typename)
        if (field.name != 'structure_needs_at_least_one_member'):
            compact['relative_paths'].append(link)
            compact['field_types'].append(type_field + array_definition_str)
            compact['field_names'].append(field.name)
    return compact
