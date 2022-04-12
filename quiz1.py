# REQUIREMENTS
# Реализовать класс поразрядного представления целого числа. Требуемые методы:
# 1) конструктор, принимающий на вход целое число def __init__(self, number): ...
# 2) сложение def __add__(self, other): ...
# 3) вычитание def __sub__(self, other): ...
# 4) изменение знака def __neg__(self)
# 5) сравнение def __eq__(self, other): ...
# 6) обратное сравнение def __ne__(self, other): ...
# 7) сравнение объектов через операнды  ">", ">=", "<", "<="
# 8) __str__ и __repr__
# операции сложения, вычитания и отрицания должны возвращать новый объект

# A)Для внутреннего представления использовать двусвязный циклический список. В качестве элементов будут цифры.
# B)Для внутреннего представления использовать массив(list). В качестве элементов будут цифры.
# C)Для внутреннего представления использовать ассоциативный массив(dict), в качестве ключей использовать разряд цифры.


from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import zip_longest
from random import randint
from typing import Iterable, Optional, Dict


class BaseLong(ABC):
    """
    класс с общей логикой для всех внутренних представлений
    """
    is_positive: bool = True

    @abstractmethod
    def __init__(self, number: Optional[int]) -> None:
        pass

    @abstractmethod
    def ciphers_from_tail(self) -> Iterable[int]:
        pass

    @abstractmethod
    def ciphers_from_head(self) -> Iterable[int]:
        pass

    @abstractmethod
    def add_cipher_to_head(self, cipher) -> None:
        pass

    @abstractmethod
    def copy(self) -> 'BaseLong':
        pass

    def _add_positives(self, other) -> 'BaseLong':
        memory = 0
        result = self.__class__(None)
        for cipher1, cipher2 in zip_longest(self.ciphers_from_tail(), other.ciphers_from_tail(), fillvalue=0):
            cur_res = cipher1 + cipher2 + memory
            result.add_cipher_to_head(cur_res % 10)
            memory = cur_res // 10
        if memory > 0:
            result.add_cipher_to_head(memory)

        return result

    def _sub_positives_first_bigger(self, other):
        if self == other:
            return self.__class__(0)
        memory = 0
        result = self.__class__(None)
        cache = 0
        for cipher1, cipher2 in zip_longest(self.ciphers_from_tail(), other.ciphers_from_tail(), fillvalue=0):
            cur_res = cipher1 - cipher2 + memory
            cipher = cur_res % 10
            if cipher == 0:
                cache += 1
            else:
                for _ in range(cache):
                    result.add_cipher_to_head(0)
                cache = 0
                result.add_cipher_to_head(cipher)
            memory = cur_res // 10
        if memory < 0:
            result.add_cipher_to_head(memory)

        return result

    def __neg__(self):
        new_one = self.copy()

        if self != self.__class__(0):
            new_one.is_positive = not self.is_positive
        return new_one

    def _sub_positives(self, other) -> 'BaseLong':
        match self > other:
            case True:
                return self._sub_positives_first_bigger(other)
            case False:
                return -other._sub_positives_first_bigger(self)

    def __sub__(self, other) -> 'BaseLong':
        match self.is_positive, other.is_positive:
            case True, True:
                return self._sub_positives(other)
            case True, False:
                return self._add_positives(-other)
            case False, True:
                return -(-self)._add_positives(other)
            case False, False:
                return -(-self)._sub_positives(-other)

    def __add__(self, other: 'BaseLong') -> 'BaseLong':
        match self.is_positive, other.is_positive:
            case True, True:
                return self._add_positives(other)
            case True, False:
                return self._sub_positives(-other)
            case False, True:
                return other._sub_positives(-self)
            case False, False:
                return -self._add_positives(other)

    def __str__(self):
        sign = '' if self.is_positive else '-'
        return sign + ''.join(map(str, self.ciphers_from_head()))

    __repr__ = __str__

    def __eq__(self, other: 'BaseLong'):
        for cipher1, cipher2 in zip_longest(self.ciphers_from_tail(), other.ciphers_from_tail(), fillvalue=0):
            if cipher1 != cipher2:
                return False

        return self.is_positive == other.is_positive

    def __gt__(self, other: 'BaseLong'):
        sign = None
        match self.is_positive, other.is_positive:
            case True, True:
                sign = True
            case True, False:
                return True
            case False, True:
                return False
            case False, False:
                sign = False

        ciphers_from_head1 = list(self.ciphers_from_head())
        ciphers_from_head2 = list(other.ciphers_from_head())

        if len(ciphers_from_head1) > len(ciphers_from_head2):
            return sign
        if len(ciphers_from_head1) < len(ciphers_from_head2):
            return not sign
        for cipher1, cipher2 in zip(ciphers_from_head1, ciphers_from_head2):
            if cipher1 > cipher2:
                return sign
            if cipher1 < cipher2:
                return not sign
        return False

    def __ge__(self, other):
        return self > other or self == other


class ArrayLong(BaseLong):

    def __init__(self, number: Optional[int]) -> None:
        if number is None:
            self._internal = []
        elif number == 0:
            self._internal = [0]
        else:
            _internal = []

            if number < 0:
                self.is_positive = False
                number = -number

            while number > 0:
                _internal.append(number % 10)
                number = number // 10

            self._internal = list(reversed(_internal))

    def ciphers_from_tail(self) -> Iterable[int]:
        yield from self._internal[::-1]

    def ciphers_from_head(self) -> Iterable[int]:
        yield from self._internal

    def add_cipher_to_head(self, cipher) -> None:
        self._internal.insert(0, cipher)

    def copy(self) -> 'BaseLong':
        new_copy = ArrayLong(None)
        new_copy._internal = self._internal.copy()
        return new_copy


class DictLong(BaseLong):

    _internal: Dict[int, int] = None

    def __init__(self, number: Optional[int]) -> None:
        self._internal = {}
        if number is not None:
            if number < 0:
                self.is_positive = False
                number = -number
            if number == 0:
                self._internal[0] = 0
            else:
                i = 0
                while number > 0:
                    self._internal[i] = number % 10
                    number = number // 10
                    i += 1

    def ciphers_from_tail(self) -> Iterable[int]:
        yield from (self._internal[i] for i in range(len(self._internal)))

    def ciphers_from_head(self) -> Iterable[int]:
        yield from (self._internal[i] for i in range(len(self._internal)-1, -1, -1))

    def add_cipher_to_head(self, cipher) -> None:
        self._internal[len(self._internal)] = cipher

    def copy(self) -> 'BaseLong':
        new_copy = DictLong(None)
        new_copy._internal = self._internal.copy()
        return new_copy


class LinkedListLong(BaseLong):

    @dataclass
    class LinkedList:

        @dataclass
        class ListNode:
            value: int
            next: Optional['LinkedListLong.LinkedList.ListNode'] = None
            previous: Optional['LinkedListLong.LinkedList.ListNode'] = None

        head: Optional['LinkedListLong.LinkedList.ListNode'] = None
        tail: Optional['LinkedListLong.LinkedList.ListNode'] = None

        def add_to_head(self, cipher):
            node = LinkedListLong.LinkedList.ListNode(cipher, self.head)
            if self.head is not None:
                self.head.previous = node

            self.head = node
            if self.tail is None:
                self.tail = node

        def copy(self):
            def copy_node(node, prev=None):
                if node is not None:
                    node_copy = LinkedListLong.LinkedList.ListNode(node.value)
                    node_copy.next = copy_node(node.next, node_copy)
                    node_copy.previous = prev
                    return node_copy

            def find_tail(node):
                if node is not None:
                    while node.next is not None:
                        node = node.next

                    return node

            new_head = copy_node(self.head)
            new_tail = find_tail(new_head)

            new_list = LinkedListLong.LinkedList(new_head, new_tail)

            return new_list

    def __init__(self, number: Optional[int]) -> None:
        self.linked_list = LinkedListLong.LinkedList()
        if number is not None:
            if number < 0:
                self.is_positive = False
                number = -number
            if number == 0:
                self.linked_list.add_to_head(0)
            else:
                i = 0
                while number > 0:
                    self.linked_list.add_to_head(number % 10)
                    number = number // 10
                    i += 1

    def ciphers_from_tail(self) -> Iterable[int]:
        node = self.linked_list.tail
        while node is not None:
            yield node.value
            node = node.previous

    def ciphers_from_head(self) -> Iterable[int]:
        node = self.linked_list.head
        while node is not None:
            yield node.value
            node = node.next

    def add_cipher_to_head(self, cipher) -> None:
        self.linked_list.add_to_head(cipher)

    def copy(self) -> 'BaseLong':
        new_obj = LinkedListLong(None)
        new_obj.linked_list = self.linked_list.copy()
        new_obj.is_positive = self.is_positive

        return new_obj


if __name__ == '__main__':

    for LongClass in (ArrayLong, DictLong, LinkedListLong):
        print(LongClass.__name__)
        for _ in range(10000):
            n1 = randint(-10000, 10000)
            n2 = randint(-10000, 10000)
            l1 = LongClass(n1)
            l2 = LongClass(n2)
            assert str(l1) == str(n1)
            assert str(l2) == str(n2)
            assert l1 == l1
            assert str(-l1) == str(-n1)
            assert str(-l2) == str(-n2)
            assert str(l1 + l2) == str(n1 + n2)
            assert str(l1 - l2) == str(n1 - n2)
            assert (l1 > l2) == (n1 > n2)
            assert (l1 < l2) == (n1 < n2)
            assert (l1 >= l2) == (n1 >= n2)
            assert (l1 <= l2) == (n1 <= n2)
