import time
import random
import math
from collections import Counter

def generate_list(maximum, itemsNo, order):
	generatedList = []
	for i in range(itemsNo, 0, -1):
		generatedList.append(round(i / itemsNo * maximum))
	if not order:
		random.shuffle(generatedList)
	return generatedList
	
def nth_digit(x, n):
	if n == 0:
		return x
	else:
		return x // 10 ** (n - 1) % 10

def bubblesort(numbers, addtl):
	end = len(numbers) - 1
	while end > 0:
		for i in range(end):
			if nth_digit(numbers[i], addtl[4]) > nth_digit(numbers[i+1], addtl[4]):
				(numbers[i], numbers[i+1]) = (numbers[i+1], numbers[i])
				time.sleep(addtl[0] ** -1)
				addtl[1] += 2
			if addtl[2].is_set():
				if addtl[3]:
					addtl[1] = 0
				return
		end -= 1

def quicksort_partition(numbers, low, high, addtl):
	# median of three: an optimisation for already sorted lists;
	# without it, python would throw a recursion error under certain conditions
	mid = math.floor((low + high) / 2)
	if numbers[mid] < numbers[low]:
		(numbers[low], numbers[mid]) = (numbers[mid], numbers[low])
	if numbers[high] < numbers[low]:
		(numbers[low], numbers[high]) = (numbers[high], numbers[low])
	if numbers[mid] < numbers[high]:
		(numbers[mid], numbers[high]) = (numbers[high], numbers[mid])
	i = low - 1
	for j in range(low, high):
		if numbers[j] <= numbers[high]:
			i += 1
			(numbers[i], numbers[j]) = (numbers[j], numbers[i])
			time.sleep(addtl[0] ** -1)
			addtl[1] += 2
		if addtl[2].is_set():
			if addtl[3]:
				addtl[1] = 0
			break
	(numbers[high], numbers[i + 1]) = (numbers[i + 1], numbers[high])
	time.sleep(addtl[0] ** -1)
	addtl[1] += 2
	return i + 1

def quicksort(numbers, addtl, low, high):
	if addtl[2].is_set():
		if addtl[3]:
			addtl[1] = 0
		return
	if low < high: # if there's more than one item in the (sub)list
		pivot = quicksort_partition(numbers, low, high, addtl) #quicksort_partition() returns the pivot
		quicksort(numbers, addtl, low, pivot - 1) #for sublist left of the pivot
		quicksort(numbers, addtl, pivot + 1, high) #for sublist right of the pivot

def bogosort(numbers, addtl):
	while not all(numbers[i+1] >= numbers[i] for i in range(len(numbers) - 1)):
		random.shuffle(numbers)
		time.sleep(addtl[0] ** -1)
		addtl[1] += len(numbers)
		if addtl[2].is_set():
			if addtl[3]:
				addtl[1] = 0
			return

def insertionsort(numbers, addtl):
		for i in range(len(numbers)):
			for j in range(i + 1, len(numbers)):
				if numbers[i] > numbers[j]:
					(numbers[i], numbers[j]) = (numbers[j], numbers[i])
					time.sleep(addtl[0] ** -1)
					addtl[1] += 2
				if addtl[2].is_set():
					if addtl[3]:
						addtl[1] = 0
					return

def countingsort(numbers, addtl):
	numbersDigitOnly = numbers.copy()
	original = numbers.copy()
	for i in range(len(numbers)):
		numbersDigitOnly[i] = nth_digit(numbers[i], addtl[4])
		numbers[i] = 0
	index = Counter(numbersDigitOnly)
	for i in range(1, max(numbersDigitOnly) + 1):
		index[i] += index[i - 1]
	for i in range(len(original) - 1, -1, -1):
		numbers[index[nth_digit(original[i], addtl[4])] - 1] = original[i]
		time.sleep(addtl[0] ** -1)
		addtl[1] += 1
		index[nth_digit(original[i], addtl[4])] -= 1
		if addtl[2].is_set():
			if addtl[3]:
				addtl[1] = 0
			return
		
def radixsort(numbers, addtl):
	for j in range(len(str(max(numbers)))):
		if addtl[2].is_set():
			return
		addtl[4] = j+1
		addtl[5](numbers, addtl)
