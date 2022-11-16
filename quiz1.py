# REQUIREMENTS
# Реализовать класс поразрядного представления целого числа произвольного размера. Требуемые методы:
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
from itertools import zip_longest, chain
from random import randint
from typing import Iterable, Optional, Dict


class BaseLong(ABC):
    """
    абстрактный класс, реализующий необходимые операции требуя реализовать в наследниках только специфичные
    для конкретной структуры данных операции
    """
    is_positive: bool = True

    @abstractmethod
    def __init__(self, number: Optional[int]) -> None:
        pass

    @abstractmethod
    def digits_from_tail(self) -> Iterable[int]:
        """обход цифр с конца(младшего разряда)"""
        pass

    @abstractmethod
    def digits_from_head(self) -> Iterable[int]:
        """обход цифр с начала(старшего разряда)"""
        pass

    @abstractmethod
    def add_digit_to_head(self, digit) -> None:
        """добавление цифры в начало числа"""
        pass

    @abstractmethod
    def copy(self) -> 'BaseLong':
        """создание копию данного объекта"""
        pass

    def _add_positives(self, other: 'BaseLong') -> 'BaseLong':
        """сложение двух чисел"""
        memory = 0
        result = self.__class__(None)
        for digit1, digit2 in zip_longest(self.digits_from_tail(), other.digits_from_tail(), fillvalue=0):
            cur_res = digit1 + digit2 + memory
            result.add_digit_to_head(cur_res % 10)
            memory = cur_res // 10
        if memory > 0:
            result.add_digit_to_head(memory)

        return result

    def _sub_positives_first_bigger(self, other):
        """вычитание числе при условии что они положительные и первый больше"""
        if self == other:
            return self.__class__(0)
        memory = 0
        result = self.__class__(None)
        cache = 0
        for digit1, digit2 in zip_longest(self.digits_from_tail(), other.digits_from_tail(), fillvalue=0):
            cur_res = digit1 - digit2 + memory
            digit = cur_res % 10
            if digit == 0:
                cache += 1
            else:
                for _ in range(cache):
                    result.add_digit_to_head(0)
                cache = 0
                result.add_digit_to_head(digit)
            memory = cur_res // 10
        if memory < 0:
            result.add_digit_to_head(memory)

        return result

    def __neg__(self):
        new_one = self.copy()

        if self != self.__class__(0):
            new_one.is_positive = not self.is_positive
        return new_one

    def _sub_positives(self, other) -> 'BaseLong':
        """вычитание двух положительных чисел"""
        match self > other:
            case True:
                return self._sub_positives_first_bigger(other)
            case False:
                return -other._sub_positives_first_bigger(self)

    def __sub__(self, other) -> 'BaseLong':
        """вычитание двух чисел"""
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
        """сложение двух чисел"""
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
        return sign + ''.join(map(str, self.digits_from_head()))

    __repr__ = __str__

    def __eq__(self, other: 'BaseLong'):
        for digit1, digit2 in zip_longest(self.digits_from_tail(), other.digits_from_tail(), fillvalue=0):
            if digit1 != digit2:
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

        digits_from_head1 = list(self.digits_from_head())
        digits_from_head2 = list(other.digits_from_head())

        if len(digits_from_head1) > len(digits_from_head2):
            return sign
        if len(digits_from_head1) < len(digits_from_head2):
            return not sign
        for digit1, digit2 in zip(digits_from_head1, digits_from_head2):
            if digit1 > digit2:
                return sign
            if digit1 < digit2:
                return not sign
        return False

    def __ge__(self, other):
        return self > other or self == other


class ArrayLong(BaseLong):
    """
    Класс поразрядного представления числа произвольного размера.
    В качестве внутреннего представления использован массив цифр
    """

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

    def digits_from_tail(self) -> Iterable[int]:
        yield from self._internal[::-1]

    def digits_from_head(self) -> Iterable[int]:
        yield from self._internal

    def add_digit_to_head(self, digit) -> None:
        self._internal.insert(0, digit)

    def copy(self) -> 'BaseLong':
        new_copy = ArrayLong(None)
        new_copy._internal = self._internal.copy()
        return new_copy


class DictLong(BaseLong):
    """
    Класс поразрядного представления числа произвольного размера.
    В качестве внутреннего представления использован dict
    """

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

    def digits_from_tail(self) -> Iterable[int]:
        yield from (self._internal[i] for i in range(len(self._internal)))

    def digits_from_head(self) -> Iterable[int]:
        yield from (self._internal[i] for i in range(len(self._internal)-1, -1, -1))

    def add_digit_to_head(self, digit) -> None:
        self._internal[len(self._internal)] = digit

    def copy(self) -> 'BaseLong':
        new_copy = DictLong(None)
        new_copy._internal = self._internal.copy()
        return new_copy


class LinkedListLong(BaseLong):
    """
    Класс поразрядного представления числа произвольного размера.
    В качестве внутреннего представления использован связный список
    """

    @dataclass
    class LinkedList:

        @dataclass
        class ListNode:
            value: int
            next: Optional['LinkedListLong.LinkedList.ListNode'] = None
            previous: Optional['LinkedListLong.LinkedList.ListNode'] = None

        head: Optional['LinkedListLong.LinkedList.ListNode'] = None
        tail: Optional['LinkedListLong.LinkedList.ListNode'] = None

        def add_to_head(self, digit):
            node = LinkedListLong.LinkedList.ListNode(digit, self.head)
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

    def digits_from_tail(self) -> Iterable[int]:
        node = self.linked_list.tail
        while node is not None:
            yield node.value
            node = node.previous

    def digits_from_head(self) -> Iterable[int]:
        node = self.linked_list.head
        while node is not None:
            yield node.value
            node = node.next

    def add_digit_to_head(self, digit) -> None:
        self.linked_list.add_to_head(digit)

    def copy(self) -> 'BaseLong':
        new_obj = LinkedListLong(None)
        new_obj.linked_list = self.linked_list.copy()
        new_obj.is_positive = self.is_positive

        return new_obj


if __name__ == '__main__':
    MAX = 100000
    MIN = -100000
    SIZE = 10000
    rnd_ints = [(randint(MIN, MAX), randint(MIN, MAX)) for _ in range(SIZE)]
    with_zeros = [(0, randint(MIN, MAX)), (randint(MIN, MAX), 0), (0, 0)]

    for long_cls in (ArrayLong, DictLong, LinkedListLong):
        print(long_cls.__name__)
        for n1, n2 in chain(with_zeros, rnd_ints):
            l1 = long_cls(n1)
            l2 = long_cls(n2)
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
