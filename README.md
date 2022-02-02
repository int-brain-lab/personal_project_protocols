# project_protocols

This repo exists to keep track of the variations of the IBL tasks that IBL researchers are implementing. 
Why you should use this repo:

. The rig is still under active development and the internal logic might change from one release to the next. By uploading your tasks here I can keep track of the changes that might break your workflow and create pull requests for you to approve with the required changes that will keep your tasks running. This way you can easily redownload and reimport your tasks after updating the rig if the update implements changes to the rig's internal logic.


To add your project task protocol follow these steps:
- Clone this repo
- Add a top level folder with your project name
- Inside this folder create a folder called **tasks** 
- Copy your "seed" task (habituation/training/biased/ephys) to the **tasks** folder
- Rename the task, this means the folder name and the main python file that implements the task logic
- Change the task however you want
- Push your changes to the repo

To install your task in your rig:
- activate the rig environment
- run `python import_project_to_rig.py -p <your_project_name>`

The import script will use Alyx to download the users and subjects linked to your project and configure your tasks on the rig. It will create a new pybpod project and configure it in `iblrig_params/<your_project_name>`

When you open pybpod the default project opened is the IBL project.

To see your project, click on open and select **<your_project_name>** that was imported by the script.
