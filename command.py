# -*- coding: utf-8 -*-
"""
Реализация паттерна Command (команда)
"""
from __future__ import absolute_import

from bivrost.base import AbstractCommand, AbstractBatch
from bivrost.mixins import HasStatus

__author__ = 'Taras Drapalyuk <taras@drapalyuk.com>'
__date__ = '18.04.2015'


class UpdateStatusCommand(AbstractCommand):
    _status = None

    def __init__(self, obj):
        self._obj = obj
        self._history = []

    def __repr__(self):
        return '<%s (id=%s)>' % (
            self.__class__.__name__,
            id(self._obj),
        )

    def execute(self):
        self._history.append(self._obj.status)
        self._obj.status = self._status

    def undo(self):
        self._obj.status = self._history.pop()

    def set_status(self, status):
        self._status = status

    def get_object(self):
        return self._obj


class MultipleUpdateStatusCommand(AbstractCommand):
    _status = None

    def __init__(self, _objects):
        self._objects = _objects
        self._history = {id(obj): [] for obj in self._objects}

    def __repr__(self):
        return '<%s (ids=%s)>' % (
            self.__class__.__name__,
            self._history.keys(),
        )

    def execute(self):
        for obj in self._objects:
            self._history[id(obj)].append(obj.status)
            obj.status = self._status

    def undo(self):
        for obj in self._objects:
            obj.status = self._history[id(obj)].pop()

    def set_status(self, status):
        self._status = status

    def add_object(self, obj):
        self._objects.append(obj)
        self._history[id(obj)] = []


class MultipleStop(MultipleUpdateStatusCommand):
    _status = "STOPPED"


class MultipleStart(MultipleUpdateStatusCommand):
    _status = "STARTED"


class MultipleArchive(MultipleUpdateStatusCommand):
    _status = "ARCHIVED"


class Stop(UpdateStatusCommand):
    _status = "STOPPED"


class Start(UpdateStatusCommand):
    _status = "STARTED"


class Archive(UpdateStatusCommand):
    _status = "ARCHIVED"


MULTIPLE_BY_SINGLE_CLASS = {
    Start: MultipleStart,
    Stop: MultipleStop,
    Archive: MultipleArchive,
}


class MyBatch(AbstractBatch):
    def execute(self):
        for command in self._batch:
            command.execute()


class UpdateStatusBatch(AbstractBatch):
    def __init__(self):
        super(UpdateStatusBatch, self).__init__()

        self._objects = []

    def execute(self):
        for command in self._prepared_batch():
            command.execute()

    def execute_batch(self):
        for command in self._batch:
            command.execute()

    def _prepared_batch(self):
        prepared_batch = []
        for command in self._batch:
            multi_command_class = MULTIPLE_BY_SINGLE_CLASS.get(command.__class__)
            if not multi_command_class:
                prepared_batch.append(command)
                continue

            command_prepared = False
            for prep_multi_command in prepared_batch:
                if isinstance(prep_multi_command, multi_command_class):
                    prep_multi_command.add_object(command.get_object())
                    command_prepared = True
                    break

            if not command_prepared:
                prep_multi_command = multi_command_class([command.get_object()])
                prepared_batch.append(prep_multi_command)

        return prepared_batch


class MyObject(HasStatus):
    pass


if __name__ == '__main__':
    import time

    N = 10 ** 3
    objects = (MyObject() for i in xrange(N))

    batch = UpdateStatusBatch()

    for o in objects:
        batch.add(Stop(o))
        batch.add(Start(o))
        batch.add(Archive(o))

    t1 = time.time()
    batch.execute_batch()
    t2 = time.time()
    batch.execute()
    t3 = time.time()

    simple = t2 - t1
    prepared = t3 - t2
    print(prepared, simple)
    print(prepared / simple)
