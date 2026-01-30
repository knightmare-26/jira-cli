import pytest
import os
import yaml
from unittest.mock import patch
from jira_ai_cli.policy_engine import PolicyEngine, DEFAULT_POLICY_FILE

# Fixture to create a temporary policy file for testing
@pytest.fixture
def temp_policy_file(tmp_path):
    policy_content = {
        "allowed_actions": ["create_ticket", "transition_ticket"],
        "allowed_transitions": {
            "OPEN": ["IN PROGRESS"],
            "IN PROGRESS": ["DONE"]
        },
        "blocked_states": ["CLOSED"],
        "similarity": {
            "lookback_days": 90,
            "min_similarity": 0.8
        }
    }
    file_path = tmp_path / DEFAULT_POLICY_FILE
    with open(file_path, "w") as f:
        yaml.dump(policy_content, f)
    return file_path

@pytest.fixture
def empty_policy_file(tmp_path):
    file_path = tmp_path / DEFAULT_POLICY_FILE
    with open(file_path, "w") as f:
        f.write("")
    return file_path

@pytest.fixture
def invalid_yaml_file(tmp_path):
    file_path = tmp_path / DEFAULT_POLICY_FILE
    with open(file_path, "w") as f:
        f.write("invalid: - yaml") # Malformed YAML
    return file_path

def test_load_policy_success(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.policy is not None
    assert policy_engine.get_allowed_actions() == ["create_ticket", "transition_ticket"]
    assert policy_engine.get_similarity_threshold() == 0.8

def test_load_policy_file_not_found(tmp_path):
    non_existent_file = tmp_path / "non_existent_policy.yaml"
    policy_engine = PolicyEngine(policy_file_path=non_existent_file)
    assert policy_engine.policy == {}
    assert policy_engine.get_allowed_actions() == []
    assert policy_engine.get_similarity_threshold() == 0.75 # Default value

def test_load_empty_policy_file(empty_policy_file):
    policy_engine = PolicyEngine(policy_file_path=empty_policy_file)
    assert policy_engine.policy == {}
    assert policy_engine.get_allowed_actions() == []

def test_load_invalid_yaml_file(invalid_yaml_file, capsys):
    policy_engine = PolicyEngine(policy_file_path=invalid_yaml_file)
    assert policy_engine.policy == {}
    assert "Error parsing policy file" in capsys.readouterr().err

def test_get_allowed_actions(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.get_allowed_actions() == ["create_ticket", "transition_ticket"]

def test_get_allowed_transitions(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    expected_transitions = {"OPEN": ["IN PROGRESS"], "IN PROGRESS": ["DONE"]}
    assert policy_engine.get_allowed_transitions() == expected_transitions

def test_get_blocked_states(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.get_blocked_states() == ["CLOSED"]

def test_get_similarity_threshold(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.get_similarity_threshold() == 0.8

def test_get_lookback_days(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.get_lookback_days() == 90

def test_is_action_allowed(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.is_action_allowed("create_ticket") is True
    assert policy_engine.is_action_allowed("add_comment") is False

def test_is_transition_allowed(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.is_transition_allowed("OPEN", "IN PROGRESS") is True
    assert policy_engine.is_transition_allowed("OPEN", "DONE") is False
    assert policy_engine.is_transition_allowed("UNKNOWN", "IN PROGRESS") is False

def test_is_state_blocked(temp_policy_file):
    policy_engine = PolicyEngine(policy_file_path=temp_policy_file)
    assert policy_engine.is_state_blocked("CLOSED") is True
    assert policy_engine.is_state_blocked("OPEN") is False
