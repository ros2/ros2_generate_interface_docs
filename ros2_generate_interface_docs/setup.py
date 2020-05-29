from setuptools import find_packages
from setuptools import setup

package_name = 'ros2_generate_interface_docs'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['setuptools'],
    package_data={'': ['templates/*']},
    zip_safe=False,
    author='Alejandro Hernández',
    author_email='ahcorde@osrfoundation.org',
    maintainer='Alejandro Hernández',
    maintainer_email='ahcorde@osrfoundation.org',
    url='https://github.com/ros2/ros2_generate_interface_docs',
    download_url='https://github.com/ros2/ros2_generate_interface_docs/releases',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Tool to generate interfaces public API documentation',
    license='Apache License, Version 2.0, BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ros2_generate_interface_docs = ' + package_name + '.main:main',
        ],
    },
)
