#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import argparse

from subprocess import call
from json import load

# TODO: Implement a SAVE function

class TMUXWorkspaceList(list):
    """
    Loads every file ending with *.json from the ~/.workspaces directory and
    create a list of available workspaces
    """

    def __init__(self, workspace_dir="~/.workspaces"):
        self.workspace_dir = os.path.expanduser(workspace_dir)

        for filename in os.listdir(self.workspace_dir):
            if filename.endswith('.json'):
                try:
                    tmp = TMUXWorkspace(os.path.join(self.workspace_dir, filename))
                except ValueError, err:
                    print "invalid json in file %s: %s" % (filename, err)
                else:
                    self.append(tmp)

    def start(self, workspacename):
        for workspace in self:
            if workspace.name == workspacename:
                workspace.create()
                return

        print "unknown workspace: %s" % (workspacename,)

    def list(self):
        return [ workspace.name for workspace in self ]


class TMUXWorkspace(object):
    """
    This is the parent class for creating a tmux workspace consisting of one
    or multiple windows and panes. Currently only working on the currently 
    ACTIVE tmux session (will be extended soon)
    """

    def __init__(self, filename):
        self.workspace = load(open(filename))
        self.name = self.workspace['workspace']
        self.windows = {}

        for window in self.workspace['windows']:
            self.windows[window['name']] = TMUXWindow(**window)

    def create(self):
        for window in self.windows:
            call(self.windows[window])
            for pane in self.windows[window].get_panes():
                call(pane)
            if self.windows[window].get_layout():
                call(self.windows[window].get_layout())


class TMUXPane(list):
    """
    Abstract representation of a tmux pane
    @split: h=horizontal split, v=vertical split
    @percentage: percentage of the split pane
    @target: target window/pane to split
    @command: command to execute in the new pane
    """

    def __init__(self, split="h", percentage=None, target=None, command=None):
        self += ['tmux', 'split-window', '-%s' % (split, )]
        if percentage is not None:
            self += ['-p', str(percentage)]
        if target is not None:
            self += ['-t', "%d" % (target, )]
        if command is not None:
            self += [command, ]

    def __str__(self):
        return " ".join(self)


class TMUXWindow(list):
    """
    Abstract representation of a tmux window
    @name: name of the new window
    @command: command to execute in the new window
    """

    def __init__(self, name=None, command=None, layout=None, panes=None):
        self.panes = []
        self.layout = layout

        self += ['tmux', 'new-window']
        if name:
            self += ['-n', name]
        if command:
            self += [command, ]
        if panes:
            for pane in panes:
                self.add_pane(TMUXPane(**pane))

    def add_pane(self, pane):
        self.panes.append(pane)

    def get_panes(self):
        return self.panes

    def get_layout(self):
        if not self.layout:
            return None

        return ['tmux', 'select-layout', self.layout]

    def __str__(self):
        return " ".join(self)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="list available workspaces", action='store_const', const=True, default=False)
    parser.add_argument("workspace", help="load workspace in tmux", nargs="?", default="default")
    args = parser.parse_args()

    workspaces = TMUXWorkspaceList()
    if args.list:
        print "\n".join(workspaces.list())
    else:
        workspaces.start(args.workspace)
