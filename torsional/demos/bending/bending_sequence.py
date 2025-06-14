import mujoco
import mujoco.viewer
import numpy as np
import time
from torsional.utils import load_model_from_arg

# Load model
model = load_model_from_arg()
data = mujoco.MjData(model)

# Actuator control direction map
sign_map = {
    "spring1a_motor": 1,
    "spring3a_motor": 1,
    "spring2c_motor": 1,
    "spring4c_motor": 1,
    "spring1c_motor": 1,
    "spring3c_motor": 1,
    "spring2a_motor": 1,
    "spring4a_motor": 1,
}

# Actuator ID lookup
actuator_ids = {name: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name) for name in sign_map.keys()}

# Define the exact actuation sequence
flat_sequence = [
    "spring1a_motor", "spring3a_motor", "spring1a_motor", "spring3a_motor",
    "spring2a_motor", "spring4a_motor", "spring2a_motor", "spring4a_motor",
    "spring1c_motor", "spring3c_motor", "spring1c_motor", "spring3c_motor",
    "spring2c_motor", "spring4c_motor", "spring2c_motor", "spring4c_motor"
]

# Wrap each actuator name in a list (since ramp() expects a list)
sequence = [[name] for name in flat_sequence]

# Parameters
dt = model.opt.timestep
steps_per_ramp = int(2.0 / dt)
steps_per_pause = int(1.0 / dt)
amplitude = 3.14

def ramp(group, direction='up'):
    for step in range(steps_per_ramp):
        frac = step / steps_per_ramp
        scale = frac if direction == 'up' else (1 - frac)
        for name in group:
            aid = actuator_ids[name]
            sign = sign_map[name]
            data.ctrl[aid] = sign * amplitude * scale
        mujoco.mj_step(model, data)
        viewer.sync()
        time.sleep(dt)

def pause():
    for _ in range(steps_per_pause):
        mujoco.mj_step(model, data)
        viewer.sync()
        time.sleep(dt)

# Run viewer with full actuation sequence
with mujoco.viewer.launch_passive(model, data) as viewer:
    for group in sequence:
        ramp(group, direction='up')
        pause()
        ramp(group, direction='down')
        pause()

print("Actuation sequence completed.")
