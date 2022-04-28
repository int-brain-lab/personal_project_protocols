# ksocha_midbrain_project
ksocha_optoProtocols - protocols compatible with IBL rigs used for optogenetics manipulations:
- during the IBL biased-blocks task: ephys rig (_iblrig_tasks_ksocha_ephysOptoChoiceWorld), behavior rig (_iblrig_tasks_ksocha_opto_biasedChoiceWorld)
- passive laser stimulation (with no visual stimulus, no reward, no sound): ephys rig (_iblrig_tasks_ksocha_ephysOptoStimulation), behavior_rig (_iblrig_ksocha_OptoStimulation)
- passive visual stimulation, same as passiveChoiceWorld (_iblrig_tasks_ksocha_ephysPassiveStimulation); it displays visual stimulation, and task-events outside of the task, in following order: spontanous activity (blank screen, no stimulation, 10min); RF Mapping (sparse noise, 5min); task-events-reply (visuals stimulus from the task, goCue sound, error noise, reward valve cliks, 40 trials, 5min)

Protocols (passiveChoiceWorld, ephysChoiceWorld, biasedChoiceWorld) were originally written by Niccolò Bonacchi for the International Brain Laboratory (IBL) project, and later modified by Karolina Socha (see description below _iblrig_tasks_ksocha_ephysOptoChoiceWorld).
The task structure (80/20 biased-blocks version) remained as described in the International Brain Laboratory et al. (eLife) 2021 https://elifesciences.org/articles/63711.

Figure 4

![image](https://user-images.githubusercontent.com/32096962/165748113-a1c5bb3c-7dd9-4fbf-953f-2d400512fb90.png)

Modifications in protocol _iblrig_tasks_ksocha_ephysOptoChoiceWorld included:
1. removing first 90 trials with 50% probability (as it is in the original IBL task for ephys recordings)
2. adding laser stimulation at different task events - LASER_STIMULATION_WHERE= ['iti', 'quiescence', 'go_cue','stimulus_on']: 
- inter-trial-interval (ITI) - laser_out_iti; 
- quiescence period - laser_out_quiescence
- visual stimulus onset - laser_out_stimulus
- goCue onset - laser_out_go_cue
3. adding prestimulus time for trials with stimulation during quiescence; eg. 300ms before visual stimulus PRESTIMULUS_TIME_LASER=0.3 - PRESTIMULUS_TIME_LASER
4. adding general laser probability - LASER_PROBABILITY
5. adding probability of laser stimulation at different task events - PROBABILITY_LASER_STIMULATION_WHERE
6. adding condition that laser stimulation occurs only for specific contrasts values during the task: 100%, 12.5%, 0%.
CONTRAST_LASER_SET = [1.0, 0.125, 0.0] (can be removed or added contrasts that originally apeared in the IBL protocol; 100%, 25%, 12.5%, 6.25%, 0%)
8. removing "poop count"
POOP_COUNT = False  # Wether to ask for a poop count at the end of the session

These values can be modified in task_settings file (lines 60-68), example:

- LASER_PROBABILITY=0.3 # PROBABILITY OF LASER (this is overall probability of laser stimulation)
- PRESTIMULUS_TIME_LASER=0.3 # time in s before visual stimulus for quiecence laser trials
- CONTRAST_LASER_SET = [1.0, 0.125, 0.0] # Laser stimulation contrast set
- LASER_STIMULATION_WHERE=['iti', 'quiescence', 'go_cue','stimulus_on']
- PROBABILITY_LASER_STIMULATION_WHERE = [0,0,0,1] # 30% of laser trials corresponds to stimulation at visual stimulus onset; sum of these values = 1 ; if [0,.5,0,.5] this means that these 30% of laser trials will be splitted equally (50%) between quiescence or stimulus_on events;

Additionally you can add information about laser stimulation type, example:
- LASER_WAVEFORM='square'
- LASER_POWER='0.25' # in mW
