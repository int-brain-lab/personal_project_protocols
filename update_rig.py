#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @File: personal_project_protocols/install.py
# @Author: Niccolo' Bonacchi (@nbonacchi)
# @Date: Wednesday, October 13th 2021, 5:05:50 pm
from pathlib import Path
import iblrig.pybpod_config as pbc


def list_personal_projects():
    """
    List all the personal projects in the repository
    """
    projects = [x.name for x in Path(__file__).parent.glob("*") if x.is_dir() and x.name != ".git"]
    return projects


def list_task_names(personal_project):
    """
    List all the tasks in a personal project
    """
    tasks = [x.name for x in Path(__file__).parent.joinpath(personal_project, 'tasks').glob("*") if x.is_dir()]
    return tasks




if __name__ == "__main__":
    # list_personal_projects
    ppout = list_personal_projects()
    assert "nate_reverse_contingency" in ppout and ".git" not in ppout
    # list_task_names
    tnout = list_task_names("nate_reverse_contingency")
    assert all(["_nmreverse_" in x for x in tnout])
    pbc.create_project("nate_reverse_contingency")
    # create board, users, subjects tasks and generic experiment w/ 1 setup per task