# MSC-26646-1, "Core Flight System Test Framework (CTF)"
#
# Copyright (c) 2019-2021 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is governed by the NASA Open Source Agreement (NOSA) License and may be used,
# distributed and modified only pursuant to the terms of that agreement.
# See the License for the specific language governing permissions and limitations under the
# License at https://software.nasa.gov/ .
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either expressed or implied.


import pytest
from unittest.mock import patch

from lib import ctf_utility
from lib.ctf_global import Global
from lib.logger import set_logger_options_from_config
from lib.plugin_manager import PluginManager
from plugins.control_flow_plugin.control_flow_plugin import ControlFlowPlugin
from plugins.variable_plugin.variable_plugin import VariablePlugin


@pytest.fixture(name="control_flow_plugin")
def _control_flow_plugin_instance():
    return ControlFlowPlugin()


def test_control_flow_plugin_init(control_flow_plugin):
    """
    Test ControlFlowPlugin initialize method
    """
    assert control_flow_plugin.initialize()
    assert control_flow_plugin.description == "CTF ControlFlow Plugin"
    assert control_flow_plugin.name == "ControlFlow Plugin"


def test_control_flow_plugin_commandmap(control_flow_plugin):
    """
    Test ControlFlowPlugin command content
    """
    assert len(control_flow_plugin.command_map) == 2
    assert "BeginLoop" in control_flow_plugin.command_map
    assert "EndLoop" in control_flow_plugin.command_map


def test_control_flow_verify_required_commands(control_flow_plugin):
    assert len(control_flow_plugin.verify_required_commands) == 0


def test_control_flow_begin_loop_pass(control_flow_plugin):
    label = "LOOP_1"
    conditions = [{"variable": "my_var", "compare": "<", "value": 20}]
    Global.label_map[label] = [1, 2, False]
    assert VariablePlugin.set_user_defined_variable('my_var', '=', 10)
    assert Global.goto_instruction_index is None
    assert control_flow_plugin.begin_loop(label, conditions)
    assert Global.goto_instruction_index is None
    Global.label_map.clear()


def test_control_flow_begin_loop_fail(control_flow_plugin):
    label = "LOOP_1"
    conditions = [{"variable": "my_var", "compare": "<", "value": 20}]
    Global.label_map[label] = [1, 20, False]
    assert VariablePlugin.set_user_defined_variable('my_var', '=', 100)
    assert Global.goto_instruction_index is None
    assert control_flow_plugin.begin_loop(label, conditions)
    assert Global.goto_instruction_index == 20
    Global.label_map.clear()


def test_control_flow_begin_loop_instruction(control_flow_plugin):
    label = "LOOP_1"
    conditions = {"instruction": "EnableCfsOutput", "data": {"target": ""}, "wait": 1}
    Global.label_map[label] = [1, 2, False]
    assert control_flow_plugin.begin_loop(label, conditions)
    Global.label_map.clear()


def test_control_flow_end_loop(control_flow_plugin):
    label = "LOOP_1"
    Global.label_map[label] = [19, 121, False]
    Global.goto_instruction_index = None
    assert control_flow_plugin.end_loop(label)
    assert Global.goto_instruction_index is None

    Global.label_map[label] = [19, 121, True]
    assert Global.goto_instruction_index is None
    assert control_flow_plugin.end_loop(label)
    assert Global.goto_instruction_index == 19
    Global.label_map.clear()
    Global.goto_instruction_index = None


def test_control_flow_control_flow_do(control_flow_plugin):
    assert control_flow_plugin.begin_loop_index is None
    Global.current_instruction_index = 10
    assert control_flow_plugin.control_flow_do()
    assert control_flow_plugin.begin_loop_index == 11
    Global.current_instruction_index = None


def test_control_flow_control_flow_goto(control_flow_plugin):
    assert control_flow_plugin.control_flow_goto(11)
    assert Global.goto_instruction_index == 11


def test_control_flow_control_flow_while(control_flow_plugin):
    assert VariablePlugin.set_user_defined_variable('my_var', '=', 10)
    assert control_flow_plugin.control_flow_while('my_var', '<', 11)

    assert VariablePlugin.set_user_defined_variable('my_var', '=', 12)
    assert control_flow_plugin.control_flow_while('my_var', '<', 11)


def test_control_flow_control_flow_conditional_goto_fail(control_flow_plugin):
    assert not control_flow_plugin.control_flow_conditional_goto('my_var', '<', 11)
    assert not control_flow_plugin.control_flow_conditional_goto('var_none', '?', 11, 'label_1')


def test_control_flow_control_flow_conditional_goto_pass(control_flow_plugin):
    assert VariablePlugin.set_user_defined_variable('my_var', '=', 10)
    Global.goto_label_map['label_1'] = 10
    Global.goto_label_map['label_2'] = 20
    assert control_flow_plugin.control_flow_conditional_goto('my_var', '<', 11, 'label_1')
    assert control_flow_plugin.control_flow_conditional_goto('my_var', '>', 11, 'label_1','label_2')
    Global.goto_label_map.clear()
    Global.goto_instruction_index = None


def test_control_flow_shutdown(control_flow_plugin):
    assert control_flow_plugin.shutdown() is None
