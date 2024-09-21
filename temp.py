def temp(minimum, maximum):
	avg = (minimum + maximum)/2
	diff_needed = (maximum - avg) * 1.5

	return avg - diff_needed, avg + diff_needed