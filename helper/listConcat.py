#!/usr/bin/env python
# -*- coding: utf-8 -*-

class listConcat:
    lists = None

    def add(self, listToAdd):
        if self.lists == None:
            self.lists = [listToAdd]
            return
        for i, l in enumerate(self.lists):
            if l[0] == listToAdd[-1]:
                self.lists[i] = listToAdd[:-1] + l
                return
            elif l[-1] == listToAdd[0]:
                self.lists[i] = l + listToAdd[1:]
                return
            elif l[0] == listToAdd[0]:
                listToAdd.reverse()
                self.lists[i] = listToAdd + l[1:]
                return
            elif l[-1] == listToAdd[-1]:
                listToAdd.reverse()
                self.lists[i] = l[:-1] + listToAdd
                return
        self.lists.append(listToAdd)

    def get(self):
        return self.lists


def testIt():
    """concats lists

    >>> a = listConcat()
    >>> a.get()
    >>> a.add([1,2,3])
    >>> a.get()
    [[1, 2, 3]]
    >>> a.add([-1,4,1])
    >>> a.get()
    [[-1, 4, 1, 2, 3]]
    >>> a.add([3,5])
    >>> a.get()
    [[-1, 4, 1, 2, 3, 5]]
    >>> a.add([2,5])
    >>> a.get()
    [[-1, 4, 1, 2, 3, 5, 2]]
    >>> a.add([-1,7])
    >>> a.get()
    [[7, -1, 4, 1, 2, 3, 5, 2]]
    """


if __name__ == "__main__":
    import doctest

    doctest.testmod()
