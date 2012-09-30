#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

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
                self.append(TMUXWorkspace(os.path.join(self.workspace_dir, filename)))

    def start(self, workspacename):
        for workspace in self:
            if workspace.name == workspacename:
                workspace.create()
                return

        raise KeyError("unknown workspace: %s" % (workspacename,))

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
            if 'command' in window.keys():
                self.windows[window['name']] = TMUXWindow(window['name'], window['command'])
            else:
                self.windows[window['name']] = TMUXWindow(window['name'])

            if 'panes' in window.keys():
                for pane in window['panes']:
                    self.windows[window['name']].add_pane(TMUXPane(**pane))

    def create(self):
        for window in self.windows:
            call(self.windows[window])
            for pane in self.windows[window].get_panes():
                call(pane)


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

    def __init__(self, name=None, command=None):
        self.panes = []

        self += ['tmux', 'new-window']
        if name:
            self += ['-n', name]
        if command:
            self += [command, ]

    def add_pane(self, pane):
        self.panes.append(pane)

    def get_panes(self):
        return self.panes

    def __str__(self):
        return " ".join(self)

if __name__ == '__main__':
    workpspaces = TMUXWorkspaceList()
    workpspaces.start('default')
