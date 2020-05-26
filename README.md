# ros2_generate_interface_docs

This package will generate the static HTML documentation for messages, services and actions.
It will create the documentation for all the available interfaces in your ROS2 workspace.
It creates a folder with the name of the package (for example: action_msgs).
In this folder it create another folders for actions, messages or services if they exists, inside each folder you will find the correspoding documentation of the interfaces.

For example:

```plain
api/html/action_msgs/
   - msg/
     - GoalInfo.html
     - GoalStatus.html
     - GoalStatus.html
   - srv/
     - CancelGoal.html
api/html/test_msgs/
  - msg/
    - Arrays.html
    - BasicTypes.html
    - BoundedSequences.html
    - Builtins.html
    - Constants.html
    - Defaults.html
    - Empty.html
    - MultiNested.html
    - Nested.html
    - Strings.html
    - UnboundedSequences.html
    - WStrings.html
  - srv/
    - Arrays.html
    - BasicTypes.html
    - Empty.html
  - action
    - Fibonacci.html
    - NestedMessage.html
```

To generate the interfaces: compile the package and execute:

```bash
ros2 run ros2_generate_interface_docs ros2_generate_interface_docs
```

Options:

 - ``--outputdir[default: 'api/']``: Output directory where the html will be placed.
