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
import sys
import time
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

    Parameters
    ----------
    raw_text: str
        content of the interface
    Returns
    -------
    raw_test_str: str
        string with the generated HTML

    """
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
    """
    Return the resource name.

    Parameters
    ----------
    resource: str
        resource name of the interface

    Returns
    -------
    value: tuple
        a tuple with the 3 part of the resource name (for example: std_msgs/msg/Bool ->
        ('std_msgs', 'msg', 'Bool'))

    """
    if '/' not in resource:
        return '', '', resource
    values = resource.split('/')
    if len(values) != 3:
        raise ValueError(...)
    return tuple(values)


def get_templates_dir():
    """
    Return template directory.

    Returns
    -------
    template directory:  str
        return the directory of the template directory

    """
    return os.path.join(os.path.dirname(__file__), _TEMPLATES_DIR)


def copy_css_style(folder_name):
    """
    Copy the css style files in the folder_name.

    Parameters
    ----------
    folder_name: str
        name of the folder where the style css files will be copied

    """
    style_css, _ = load_template('styles.css')
    with open(os.path.join(folder_name, 'styles.css'), 'w') as f:
        f.write(style_css)

    msg_style_css, _ = load_template('msg-styles.css')
    with open(os.path.join(folder_name, 'msg-styles.css'), 'w') as f:
        f.write(msg_style_css)


def load_template(filename):
    """
    Look up file within rosdoc ROS package.

    return its content, may sys.exit on error.
    Contents are cached with filename as key.

    Parameters
    ----------
    filename: str
        name of the template to be loaded

    Returns
    -------
    content: str
        cached file contents
    filename: str
        filename of the template concat with the template directory

    """
    filename = os.path.join(get_templates_dir(), filename)
    if not os.path.isfile(filename):
        sys.stderr.write("Cannot locate template file '%s'\n" % (filename))
        sys.exit(1)
    with open(filename, 'r') as f:
        content = f.read()
        if not content:
            raise Exception("Template file '%s' is empty\n" % (filename))
        return content, filename


def generate_doc(interface, interface_template, file_output_path, doc_dic, generate_text_from_spec):
    """
    Generate msg documentation.

    This function write in a file the message static HTML site.

    Parameters
    ----------
    interface: str
        name of the interface
    interface_template: str
        name of the template
    file_output_path: str
        name of the file where the template will be written once filled
    doc_dic: dict
        dictionary with the data to field the index template

    generate_text_from_spec: function

    """
    package, interface_type, base_type = resource_name(interface)
    file_path = get_interface_path(interface)
    with open(file_path, 'r', encoding='utf-8') as h:
        spec = h.read().rstrip()

    compact_definition = generate_text_from_spec(package, base_type, spec)
    doc_dic['raw_text'] = generate_raw_text(spec)
    write_template(interface_template, {**doc_dic, **compact_definition}, file_output_path)


def generate_index(package, file_directory, interfaces):
    """
    Generate the message index page.

    Parameters
    ----------
    package: str
        package anme
    file_directory: str
        directory where the index site will be located
    interfaces: str[]
        list the the interfaces associated with the package

    """
    package_message_dic = {}
    package_message_dic['package'] = package
    package_message_dic['date'] = str(time.strftime('%a, %d %b %Y %H:%M:%S'))
    if interfaces:
        package_message_dic['links'] = [package + '/' + msg + '.html' for msg in interfaces]
        package_message_dic['interface_list'] = interfaces
    file_output_path = os.path.join(file_directory, 'index-msg.html')
    write_template('msg-index.html.em', package_message_dic, file_output_path)


def write_template(template_name, data, output_file):
    """
    Write the data in the template.

    Parameters
    ----------
    template_name: str
        name of the template to write
    data:
        data that is used to fill the template
    output_file: str
        path where the file will be written

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
        if os.path.exists(output_file):
            os.remove(output_file)
        print(f"{e.__class__.__name__} when expanding '{template_name}' into "
              f"'{output_file}': {e}", file=sys.stderr)
        raise

    content = output.getvalue()
    interpreter.shutdown()

    with open(os.path.join(output_file), 'w') as f:
        f.write(content)


def generate_compact_definition(imported_interface, indent, get_slot_types):
    """
    Create the compact definition dictionary.

    This function remove all the common dict keys to get all the contants in the message
    dictionary. Then it will generate a dictionary will the contants and field of the message.
    If the message is based in other message, then this text will contain a link to this
    interface.

    Parameters
    ----------
    imported_interface: obj
        class with all the data about the interface
    indent: int
        number of indentations to add to the generated text
    get_slot_types: function
        function that returns an OrderedDict of the slot types of a message.

    Returns
    -------
    compact: dict
        Dictionary with the compact definition (constanst and message with links)

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
    for field in fields.keys():
        if(fields[field] not in BASIC_TYPES and
           'string' not in fields[field]):
            slot_type = get_slot_types(imported_interface)[field]
            if(isinstance(slot_type, AbstractNestedType)):
                if(isinstance(slot_type.value_type, NamespacedType)):
                    pkg_name, in_type, msg_name = map(str,
                                                      slot_type.value_type.namespaced_name())
                    compact['links'].append(pkg_name + '/msg/' + msg_name + '.html')
                    compact['field_types'].append('/'.join(slot_type.value_type.namespaced_name()))
                    compact['field_names'].append(field)
            else:
                pkg_name, msg_name = fields[field].split('/')
                compact['links'].append(pkg_name + '/msg/' + msg_name + '.html')
                compact['field_types'].append(fields[field])
                compact['field_names'].append(msg_name)
        else:
            compact['links'].append('')
            compact['field_types'].append(fields[field])
            compact['field_names'].append(field)
    return compact
