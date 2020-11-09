import time
import random

def generate_list(maximum, itemsNo):
	generatedList = []
	i = 1
	while i <= itemsNo:
		generatedList.append(round(i / itemsNo * maximum))
		i += 1
	random.shuffle(generatedList)
	return generatedList

def bubblesort(numbers, fps):
	end = len(numbers) - 1
	while end > 0:
		for i in range(end):
			if numbers[i] > numbers[i+1]:
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
