#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File: import_project_protocols_to_rig.py
# @Author: Niccolo' Bonacchi (@nbonacchi)
# @Date: Wednesday, October 13th 2021, 5:05:50 pm
import shutil
from pathlib import Path

import iblrig.path_helper as ph
import iblrig.pybpod_config as pbc
from pybpodgui_api.models.project import Project


def list_projects():
    """
    List all the personal projects in the repository
    """
    projects = [x for x in Path(__file__).parent.glob("*") if x.is_dir() and x.name != ".git"]
    return projects


def list_repo_tasks(project_name):
    """
    List all the tasks in a personal project
    """
    projects = list_projects()
    matches = [project_name in str(x) for x in projects]
    if not any(matches):
        print(f"No project found with name: {project_name}")
        return
    project_path = projects[matches.index(True)]
    tasks = [x for x in project_path.joinpath('tasks').glob("*") if x.is_dir()]
    return tasks


# def copy_as_folder(src_folder_to_copy, to_dst_folder_path, overwrite=False):
#     """
#     Copy a folder as a folder to a destination folder
#     Will create the src_folder name in the dst_folder
#     Output should be the same as dragging a folder to another one.

#     ./somewhere/src_folder/*
#     ./somewhere/dst_folder/*

#     ./somewhere/dst_folder/src_folder_copy/*
#     """
#     src_folder = Path(src_folder_to_copy)
#     dst_folder = Path(to_dst_folder_path).joinpath(src_folder.name)
#     if overwrite:
#         shutil.rmtree(dst_folder)
#     shutil.copytree(src_folder, dst_folder)
#     print(f"  Copied {src_folder} to {dst_folder}")


# def copy_project_tasks_files(project_name):
#     """Copy all files in project_protocols/{project_name}/tasks/* folder to
#     iblrig_params_path/{project_name}/tasks/* folder
#     """

#     iblrig_params_path = Path(ph.get_iblrig_params_folder())
#     iblrig_params_tasks_path = iblrig_params_path / project_name / "tasks"
#     project_protocols_tasks_path = iblrig_params_path.parent.joinpath("project_protocols", project_name, "tasks")
#     print(f"\nCopying {project_name} tasks files to {iblrig_params_tasks_path}")
#     copy_as_folder(project_protocols_tasks_path, iblrig_params_tasks_path)
#     print("Done")


def copy_task_files(project_name, task_name):
    """Copy all files in project_protocols/{project_name}/tasks/{task_name} folder to
    iblrig_params_path/{project_name}/tasks/{task_name} folder
    """

    iblrig_params_path = Path(ph.get_iblrig_params_folder())

    dst_iblrig_params_project_tasks_path = iblrig_params_path.joinpath(project_name, "tasks")

    for src_task_path in list_repo_tasks(project_name):
        dst_task_path = dst_iblrig_params_project_tasks_path / src_task_path.name
        src_files = [x for x in src_task_path.rglob('*')]
        dirs = [x for x in src_files if x.is_dir()]
        [dst_task_path.mkdir(parents=True, exist_ok=True) for x in dst_task_path.parents]
        print(f"Copying {task_name} files to {dst_task_path}")
        for f in src_files:
            shutil.copy(f, dst_task_path)
            print(f"  Copied {f} to {dst_task_path}")
    print("Done")  # XXX: copy recursivelly if dir is found


def create_project_tasks(project_name):
    """
    Create all the tasks in a personal project
    """
    project_folder = Path(ph.get_iblrig_params_folder()).joinpath(project_name)
    p = Project()
    p.load(project_folder)
    for task_path in list_repo_tasks(project_name):
        task_name = task_path.name
        print(f"Creating task {task_name}")
        task = p.find_task(task_name)
        task = p.create_task()
        task.name = task_name
        p.save(project_folder)
        print(f"Created task: {task_name}")
    print("Done")


def create_project_experiment(project_name):
    project_folder = Path(ph.get_iblrig_params_folder()).joinpath(project_name)
    p = Project()
    p.load(project_folder)
    exp = p.create_experiment()
    exp.name = "run_task_protocols"
    p.save(project_folder)
    print(f"Created experiment: {exp.name}")
    tasks = list_repo_tasks(project_name)
    for task_path in tasks:
        setup = exp.create_setup()
        setup.name = task_path.name
        setup.task = task_path.name
        setup.board = p.boards[0].name
        # setup += subj
        setup.detached = True
        p.save(project_folder)
        print(f"    Created setup: {setup.name} in {exp.name}")


def copy_project_protocols_files(project_name):
    for task in list_repo_tasks(project_name):
        copy_task_files(project_name, task)

# XXX: review!
def create_project(project_name):
    """
    Create a new project
    """
    project_folder = Path(ph.get_iblrig_params_folder()).joinpath(project_name)
    p = Project()
    p.load(project_folder)
    p.name = project_name
    p.save(project_folder)
    print(f"Created project: {project_name}")
    create_project_tasks(project_name)
    create_project_experiment(project_name)
    copy_project_protocols_files(project_name)


if __name__ == "__main__":
    # test the list of list_personal_projects
    ppout = list_projects()
    assert any(["ibl_fiberfluo_pilot_01" in p.name for p in ppout])
    assert any([".git" not in p.name for p in ppout])
    # test the list_task_names for one project
    tnout = list_repo_tasks("ibl_fiberfluo_pilot_01")
    assert all(["NPH" in x.name for x in tnout])
    # test the copy_as_folder function
    # src = Path('src_folder')
    # dst = Path('dst_folder')
    # copy_as_folder(src, dst)
    # assert dst.joinpath('src_folder').exists()
    # cleanup
    # src.rmdir()
    # shutil.rmtree(dst)
    # test_creation of existing project
    pbc.create_custom_project_from_alyx("ibl_fiberfluo_pilot_01")
    # create tasks
    create_project_tasks("ibl_fiberfluo_pilot_01")
    # move files
    copy_project_protocols_files("ibl_fiberfluo_pilot_01")
    # create experiments
    create_project_experiment("ibl_fiberfluo_pilot_01")
    # create board, users, subjects tasks and generic experiment w/ 1 setup per task
