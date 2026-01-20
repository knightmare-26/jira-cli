import yaml
import os
import click

DEFAULT_POLICY_FILE = "policy.yaml"

class PolicyEngine:
    def __init__(self, policy_file_path=None):
        self.policy_file_path = policy_file_path if policy_file_path else DEFAULT_POLICY_FILE
        self.policy = self._load_policy()

    def _load_policy(self):
        """
        Loads the policy from the YAML file.
        """
        if not os.path.exists(self.policy_file_path):
            click.echo(f"Warning: Policy file not found at {self.policy_file_path}. Using empty policy.", err=True)
            return {}
        
        try:
            with open(self.policy_file_path, 'r') as f:
                policy_data = yaml.safe_load(f)
            click.echo(f"Policy loaded from {self.policy_file_path}", err=False)
            return policy_data if policy_data is not None else {}
        except yaml.YAMLError as e:
            click.echo(f"Error parsing policy file {self.policy_file_path}: {e}", err=True)
            return {}

    def get_allowed_actions(self):
        return self.policy.get("allowed_actions", [])

    def get_allowed_transitions(self):
        return self.policy.get("allowed_transitions", {})

    def get_blocked_states(self):
        return self.policy.get("blocked_states", [])

    def get_similarity_threshold(self):
        return self.policy.get("similarity", {}).get("min_similarity", 0.75) # Default from PRD

    def get_lookback_days(self):
        return self.policy.get("similarity", {}).get("lookback_days", 60) # Default from PRD

    def is_action_allowed(self, action_type):
        return action_type in self.get_allowed_actions()

    def is_transition_allowed(self, from_state, to_state):
        allowed_transitions_from_state = self.get_allowed_transitions().get(from_state, [])
        return to_state in allowed_transitions_from_state

    def is_state_blocked(self, state):
        return state in self.get_blocked_states()

    def get_policy_config(self):
        return self.policy
