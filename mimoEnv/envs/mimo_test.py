import numpy as np

from gym import utils

from mimoEnv.envs.mimo_env import MIMoEnv, MIMO_XML


# Dictionary with body_names as keys,
TOUCH_PARAMS = {
    "left_toes": 0.010,
    "right_toes": 0.010,
    "left_foot": 0.015,
    "right_foot": 0.015,
    "left_lower_leg": 0.038,
    "right_lower_leg": 0.038,
    "left_upper_leg": 0.027,
    "right_upper_leg": 0.027,
    "hip": 0.025,
    "lower_body": 0.025,
    "upper_body": 0.030,
    "head": 0.013,
    "left_eye": 1.0,
    "right_eye": 1.0,
    "left_upper_arm": 0.024,
    "right_upper_arm": 0.024,
    "left_lower_arm": 0.024,
    "right_lower_arm": 0.024,
    "left_hand": 0.007,
    "right_hand": 0.007,
    "left_fingers": 0.002,
    "right_fingers": 0.002,
}

VISION_PARAMS = {
    "eye_left": {"width": 400, "height": 300},
    "eye_right": {"width": 400, "height": 300}
}

VESTIBULAR_PARAMS = {
    "sensors": ["vestibular_acc", "vestibular_gyro"]
}


class MIMoEnvDummy(MIMoEnv):

    def __init__(self,
                 model_path=MIMO_XML,
                 initial_qpos={},
                 n_actions=40,  # Currently hardcoded
                 n_substeps=2,
                 touch_params=None,
                 vision_params=None,
                 vestibular_params=None,
                 goals_in_observation=True,
                 done_active=False):

        self.steps = 0

        super().__init__(model_path=model_path,
                         initial_qpos=initial_qpos,
                         n_actions=n_actions,
                         n_substeps=n_substeps,
                         touch_params=touch_params,
                         vision_params=vision_params,
                         vestibular_params=vestibular_params,
                         goals_in_observation=goals_in_observation,
                         done_active=done_active)

    def _get_obs(self):
        """Returns the observations."""
        obs = super()._get_obs()

        self.vision.save_obs_to_file(directory="imgs", suffix="_" + str(self.steps))
        self.steps += 1

        return obs

    def _set_action(self, action):
        ctrlrange = self.sim.model.actuator_ctrlrange
        actuation_range = (ctrlrange[:, 1] - ctrlrange[:, 0]) / 2.0
        actuation_center = (ctrlrange[:, 1] + ctrlrange[:, 0]) / 2.0
        self.sim.data.ctrl[:] = actuation_center + action * actuation_range
        self.sim.data.ctrl[:] = np.clip(
            self.sim.data.ctrl, ctrlrange[:, 0], ctrlrange[:, 1]
        )

    def _is_success(self, achieved_goal, desired_goal):
        """Indicates whether or not the achieved goal successfully achieved the desired goal."""
        # TODO: All of it
        return False

    def _is_failure(self, achieved_goal, desired_goal):
        return False

    def _sample_goal(self):
        """Samples a new goal and returns it."""
        # TODO: Actually sample a goal
        return np.zeros(self._get_proprio_obs().shape)

    def _get_achieved_goal(self):
        """Get the goal state actually achieved in this episode/timeframe."""
        # TODO: All of it
        return np.zeros(self._get_proprio_obs().shape)

    def compute_reward(self, achieved_goal, desired_goal, info):
        # TODO: Actually compute a reward
        return 0

    def _render_callback(self):
        """A custom callback that is called before rendering. Can be used
        to implement custom visualizations.
        """
        pass

    def _step_callback(self):
        """A custom callback that is called after stepping the simulation. Can be used
        to enforce additional constraints on the simulation state.
        """
        pass


class MIMoTestEnv(MIMoEnvDummy, utils.EzPickle):
    def __init__(
        self,
    ):
        utils.EzPickle.__init__(
            self
        )
        MIMoEnvDummy.__init__(
            self,
            model_path=MIMO_XML,
            touch_params=TOUCH_PARAMS,
            vision_params=VISION_PARAMS,
            vestibular_params=VESTIBULAR_PARAMS,
            goals_in_observation=False,
            done_active=True
        )
