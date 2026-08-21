import random
import time
from typing import Callable

MIN_VALUE = 0
MAX_VALUE = 10500


def generate_array(length: int) -> list[int]:
    array = []
    for _ in range(length):
        array.append(random.randint(MIN_VALUE, MAX_VALUE))
    return array


def swap(array: list[int], i: int, j: int) -> None:
    aux = array[i]
    array[i] = array[j]
    array[j] = aux


def bubble_sort(array: list[int]) -> list[int]:
    n = len(array)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if array[j] > array[j + 1]:
                swap(array, j, j + 1)
                swapped = True
        if not swapped:
            break
    return array


def insertion_sort(array: list[int]) -> list[int]:
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        while j >= 0 and array[j] > key:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key
    return array

def exec_sort(func: Callable[[list[int]], list[int]], arrays: list[list[int]]) -> dict:
    result = {"unsorted": {}, "sorted": {}}
    sorted_arrays = []

    for array in arrays:
        data = array[:]
        start = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - start
        result["unsorted"][len(data)] = {
            "sort": func.__name__,
            "time_ms": elapsed * 1000,
        }
        sorted_arrays.append(data)

    for array in sorted_arrays:
        data = array[:]
        start = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - start
        result["sorted"][len(data)] = {
            "sort": func.__name__,
            "time_ms": elapsed * 1000,
            "sorted_array": data
        }

    return result


def main() -> None:
    # unsorted_arrays = [generate_array(n) for n in (1000, 2000, 5000, 10000, 50000, 100000, 500000, 10000000)]
    # print(exec_sort(bubble_sort, unsorted_arrays))
    
    unsorted_arrays = [generate_array(n) for n in (2, 10)]

    print(exec_sort(bubble_sort, unsorted_arrays))
    exec_sort(insertion_sort, unsorted_arrays)


if __name__ == "__main__":
    main()
