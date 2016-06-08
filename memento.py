# -*- coding: utf-8 -*-
"""
    Реализация паттерна Memento (хранитель)
"""
import copy

__author__ = 'Taras Drapalyuk <taras@drapalyuk.com>'
__date__ = '20.05.2015'


class Memento(object):
    """
        Хранитель состояния объекта
    """
    def __new__(cls, obj, deep=False):
        state = (copy.deepcopy if deep else copy.copy)(obj.__dict__)

        def restore():
            obj.__dict__ = state

        return restore


class Transaction(object):
    """
        Реализует транзакционность с помощью хранителя состояний (Memento)
    """
    deep = True

    def __init__(self, *targets):
        self.targets = targets
        self.states = []
        self.commit()

    def commit(self):
        self.states = [Memento(target, self.deep) for target in self.targets]

    def rollback(self):
        for restore_sate in self.states:
            restore_sate()


class MyClass(object):
    a = 1


if __name__ == '__main__':
    a = MyClass()
    b = MyClass()
    b.b = range(10)
    t = Transaction(a, b)

    a.a = {1: {1: 2}}
    b.b.append(222)
    print(a.a)
    print(b.b)
    t.commit()
    print('<- commit')

    a.a = {2: 3}
    a.a = {3: {3: 4}}
    b.b.append(111)
    print(a.a)
    print(b.b)
    t.rollback()
    print('<- rollback')
    print(a.a)
    print(b.b)
