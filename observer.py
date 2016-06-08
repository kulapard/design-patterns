# -*- coding: utf-8 -*-
"""
Реализация паттерна Observer (наблюдатель)
"""
from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

__author__ = 'Taras Drapalyuk <taras@drapalyuk.com>'
__date__ = '17.04.2015'


class AbstractSubject(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._observers = set()
        self._changed = False

    def register_observer(self, observer):
        if isinstance(observer, AbstractObserver):
            self._observers.add(observer)

    def unregister_observer(self, observer):
        if isinstance(observer, AbstractObserver):
            self._observers.remove(observer)

    def notify_observers(self):
        # Оповещаем наблюдателей, если объект изменился
        if self.has_changed():
            for observer in self._observers:
                observer.update(self)

    def set_changed(self):
        self._changed = True

    def has_changed(self):
        return self._changed

    def clear_changed(self):
        self._changed = False


class AbstractObserver(object):
    __metaclass__ = ABCMeta

    def subscribe(self, *subjects):
        for subject in subjects:
            subject.register_observer(self)

    def unsubscribe(self, *subjects):
        for subject in subjects:
            subject.unregister_observer(self)

    @abstractmethod
    def update(self, subject, *args, **kwargs):
        pass


class SubjectMixin(AbstractSubject):
    pass


# TEST ########################################################################
class MySubject(AbstractSubject):
    def __init__(self):
        super(MySubject, self).__init__()
        self._data = dict()

    def __setitem__(self, key, value):
        print('__setitem__ MySubject')
        self._data[key] = value
        self.set_changed()
        self.notify_observers()


class MyObserver(AbstractObserver):
    def __init__(self):
        print('init %s' % self.__class__.__name__)

    def update(self, subject, *args, **kwargs):
        print('Observer %s catched update %s: args=%s, kwargs=%s'
              % (self, subject, args, kwargs))


if __name__ == "__main__":
    s1 = MySubject()
    s2 = MySubject()
    o1 = MyObserver()
    o2 = MyObserver()

    s_list = [s1, s2]

    o1.subscribe(*s_list)
    o2.subscribe(*s_list)

    s1['a'] = None
    s2['a'] = 'b'
    o2.unsubscribe(*s_list)
    s1['a'] = 'c'
    s1['a'] = 'd'
