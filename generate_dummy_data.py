from random import uniform, randint

num_of_files = int(input("How many files of dummy data would you like: \n"))

for i in range(1, num_of_files+1):
	with open(f"dummy_file_{i}.txt", "w") as d_f:
		num_rows = randint(10, 30)
		d_f.write("0 3.60 10.00 25.00 10.00\n")
		for t in range(1, num_rows):
			voltage_min, voltage_max = 2.07, 4.6 #actual range from 2.50 to 4.2 but you want transitions
			curr_min, curr_max = 0.0, 25.0 #actual range from 0 to 20
			temp_min, temp_max = -11.0, 56.0 #actual range from 0 to 45
			if t>num_rows/2:
				curr_min, curr_max = 0.0, 150.0 #actual range from 0 to 120
				temp_min, temp_max = -40.0, 80.0 #actual range from -20 to 60
			battery_capacity = 10.00 #10 Ah
			d_f.write(str(t) + " " + str(round(uniform(voltage_min, voltage_max), 2)) + " " + str(round(uniform(curr_min, curr_max), 2)) + " " + str(round(uniform(temp_min, temp_max), 2)) + " " + str(battery_capacity) + "\n")