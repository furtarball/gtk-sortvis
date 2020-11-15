import time
import random
from collections import Counter

def generate_list(maximum, itemsNo):
	generatedList = []
	i = 1
	while i <= itemsNo:
		generatedList.append(round(i / itemsNo * maximum))
		i += 1
	random.shuffle(generatedList)
	return generatedList
	
def nth_digit(x, n):
	if n == 0:
		return x
	else:
		return x // 10 ** (n - 1) % 10

def bubblesort(numbers, fps, digit):
	end = len(numbers) - 1
	while end > 0:
		for i in range(end):
			if nth_digit(numbers[i], digit) > nth_digit(numbers[i+1], digit):
				(numbers[i], numbers[i+1]) = (numbers[i+1], numbers[i])
				time.sleep(fps ** -1)
		end -= 1

def quicksort_partition(numbers, low, high, fps):
	i = low - 1
	for j in range(low, high):
		if numbers[j] <= numbers[high]:
			i += 1
			(numbers[i], numbers[j]) = (numbers[j], numbers[i])
			time.sleep(fps ** -1)
	(numbers[high], numbers[i + 1]) = (numbers[i + 1], numbers[high])
	time.sleep(fps ** -1)
	return i + 1

def quicksort(numbers, low, high, fps):
	if low < high: # if there's more than one item in the (sub)list
		pivot = quicksort_partition(numbers, low, high, fps) #quicksort_partition() returns the pivot
		quicksort(numbers, low, pivot - 1, fps) #for sublist left of the pivot
		quicksort(numbers, pivot + 1, high, fps) #for sublist right of the pivot

def bogosort(numbers, fps):
	while not all(numbers[i+1] >= numbers[i] for i in range(len(numbers) - 1)):
		random.shuffle(numbers)
		time.sleep(fps ** -1)

def insertionsort(numbers, fps):
		for i in range(len(numbers)):
			for j in range(i + 1, len(numbers)):
				if numbers[i] > numbers[j]:
					(numbers[i], numbers[j]) = (numbers[j], numbers[i])
					time.sleep(fps ** -1)

# NOT an accurate visual representation. Counting sort does not and cannot work on the
# original, unsorted list. Here it uses a copy instead of creating an empty one.
def countingsort(numbers, fps, digit): # assign digit as 0 to disable radixsort mode
	numbersDigitOnly = numbers.copy()
	for i in range(len(numbers)):
		numbersDigitOnly[i] = nth_digit(numbers[i], digit)
	index = Counter(numbersDigitOnly)
	original = numbers.copy()
	for i in range(1, max(numbersDigitOnly) + 1):
		index[i] += index[i - 1]
	for i in range(len(original) - 1, -1, -1):
		numbers[index[nth_digit(original[i], digit)] - 1] = original[i]
		time.sleep(fps ** -1)
		index[nth_digit(original[i], digit)] -= 1
		
def radixsort(numbers, fps, subroutine):
	for j in range(len(str(max(numbers)))):
		subroutine(numbers, fps, j+1)
