#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Niccolò Bonacchi
# @Date: Friday, November 15th 2019, 12:05:29 pm
import logging
import sys
import time

import numpy as np
import random
import usb
from ibllib.graphic import popup
from pybpodapi.protocol import Bpod, StateMachine

import iblrig.bonsai as bonsai
import iblrig.frame2TTL as frame2TTL
import iblrig.iotasks as iotasks
import iblrig.misc as misc
import iblrig.params as params
import task_settings
import user_settings
from iblrig.bpod_helper import BpodMessageCreator, bpod_lights
from iblrig.rotary_encoder import MyRotaryEncoder
from session_params import SessionParamHandler

log = logging.getLogger("iblrig")
log.setLevel(logging.INFO)

global sph
sph = SessionParamHandler(task_settings, user_settings)

PARAMS = params.load_params_file()

PULSE_DUR = 0.0005  # pulse width to Cyclopse in s

# get bpod
bpod = Bpod()
sma = StateMachine(bpod)
# Build messages
msg = BpodMessageCreator(bpod)
bpod = msg.return_bpod()
if sph.OPTO_DURATION > 1:
    raise NameError('Opto duration cannot be longer than 1 second (this is hard coded in the driver)')

# Make global timers
sma.set_global_timer(timer_id=1, timer_duration=0.05, channel='BNC2')

# Generate stimulation sequence
opto_hz = np.tile(np.repeat(sph.OPTO_HZ, sph.OPTO_TIMES), len(sph.OPTO_POWER))
opto_power = np.repeat(sph.OPTO_POWER, len(sph.OPTO_HZ) * sph.OPTO_TIMES)
shuffled_indices = np.random.permutation(opto_hz.shape[0])
opto_hz = opto_hz[shuffled_indices]
opto_power = opto_power[shuffled_indices]

# Make lookup table how many pulses to send (hardcoded in LED driver)
opto_hz_pulses = [1, 5, 10, 25, 1, 5, 10, 25]
opto_power_pulses = [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5]

# Spontaneous activity
log.info("Starting %d minutes of spontaneous activity" % (sph.SPONTANEOUS_DURATION / 60))
time.sleep(sph.SPONTANEOUS_DURATION)

# start opto stim
log.info("Starting optogenetic stimulation")
for i, (hz, power) in enumerate(zip(opto_hz, opto_power)):
    log.info("Stimulation %d of %d (%d Hz, %.1f power)" % (i + 1, opto_hz.shape[0], hz, power))
    sma = StateMachine(bpod)  # initialize state machine
    time.sleep(misc.texp(factor=sph.ISI_MEAN, min_=sph.ISI_MIN, max_=sph.ISI_MAX))  # random isi

    # Look up how many pulses to send
    n_pulses = np.where((opto_hz_pulses == hz) & (opto_power_pulses == power))[0][0] + 1

    # If only one pulse has to be sent, do that, otherwise go into loop mode
    if n_pulses == 1:
        sma.add_state(
            state_name="opto_on",
            state_timer=PULSE_DUR,
            output_actions=[("BNC2", 255)],  # To FPGA
            state_change_conditions={"Tup": "exit"})
    else:
        sma.set_global_timer(timer_id=1, timer_duration=PULSE_DUR, on_set_delay=PULSE_DUR,
                             loop_mode=n_pulses, channel='BNC2')
        sma.add_state(
            state_name='TimerTrig',  # Trigger global timer
            state_timer=0,
            output_actions=[(Bpod.OutputChannels.GlobalTimerTrig, 1)],
            state_change_conditions={"Tup": "exit"})
    bpod.send_state_machine(sma)
    bpod.run_state_machine(sma)  # Locks until state machine 'exit' is reached

bpod.close()
# Turn bpod light's back on
bpod_lights(PARAMS["COM_BPOD"], 1)
# Close Bonsai stim
log.info("Protocol finished")

if __name__ == "__main__":
    pregenerated_session_num = "mock"
