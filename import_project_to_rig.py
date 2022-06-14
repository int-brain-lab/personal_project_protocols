#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File: import_project_protocols_to_rig.py
# @Author: Niccolo' Bonacchi (@nbonacchi)
# @Date: Wednesday, October 13th 2021, 5:05:50 pm
import argparse
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
    tasks = [x for x in project_path.joinpath("tasks").glob("*") if x.is_dir()]
    return tasks


def copy_task_files(project_name, task_name):
    """Copy all files in project_protocols/{project_name}/tasks/{task_name} folder to
    iblrig_params_path/{project_name}/tasks/{task_name} folder
    """

    iblrig_params_path = Path(ph.get_iblrig_params_folder())

    dst_iblrig_params_project_tasks_path = iblrig_params_path.joinpath(project_name, "tasks")

    for src_task_path in list_repo_tasks(project_name):
        dst_task_path = dst_iblrig_params_project_tasks_path / src_task_path.name
        src_files = [x for x in src_task_path.rglob("*")]
        dirs = [x for x in src_files if x.is_dir()]
        [src_files.pop(src_files.index(x)) for x in dirs]
        [x.mkdir(parents=True, exist_ok=True) for x in dirs]
        dst_task_path.mkdir(parents=True, exist_ok=True)
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


def create_project_experiment_and_setups(project_name):
    project_folder = Path(ph.get_iblrig_params_folder()).joinpath(project_name)
    p = Project()
    p.load(project_folder)
    exp = p.create_experiment()
    exp.name = "run_task_protocols"
    p.save(project_folder)
    print(f"Created experiment: {exp.name}")
    tasks = list_repo_tasks(project_name)
    if p.boards in [None, []]:
        p.create_board()
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


def create_project(project_name):
    """
    Create a new project
    """
    # board, users and subjects from alyx
    pbc.create_custom_project_from_alyx(project_name)
    # TODO: if not work, make locally with default names
    # create empty tasks in pybpod
    create_project_tasks(project_name)
    # copy files from project_protocols to iblirg_params/<project_name>/tasks
    copy_project_protocols_files(project_name)
    # create experiment and setups of board, users, subjects, and tasks
    create_project_experiment_and_setups(project_name)


def test_import_project_to_rig():
    """
    Test import of project_protocols to rig
    """
    project_name = "example_project"
    task_name = "_example_tasks_passive"
    # test the list of list_personal_projects
    ppout = list_projects()
    assert any([project_name in p.name for p in ppout])
    assert any([".git" not in p.name for p in ppout])
    # test the list_task_names for one project
    tnout = list_repo_tasks(project_name)
    assert any([task_name in x.name for x in tnout])
    # create temporary project
    pbc.create_project(project_name)
    pbc.create_user(project_name)
    pbc.create_subject(project_name, "_iblrig_test_mouse")
    # create tasks
    create_project_tasks(project_name)
    # move files
    copy_project_protocols_files(project_name)
    # create experiments
    create_project_experiment_and_setups(project_name)
    # cleanup
    shutil.rmtree(Path(ph.get_iblrig_params_folder()).joinpath(project_name))
    print("\nIf you can read this the test has passed!\n")


if __name__ == "__main__":
    # Create CLI
    parser = argparse.ArgumentParser(description="Create a new project")
    # Add optional project_name parameter
    parser.add_argument(
        "-p",
        help="Name of the project to create",
        type=str,
        default="example_project",
        required=False,
    )
    # Add optional arguments to run test
    parser.add_argument("--test", action="store_true", help="Run test")

    args = parser.parse_args()
    # Run
    if args.test:
        test_import_project_to_rig()
    else:
        create_project(args.p)
