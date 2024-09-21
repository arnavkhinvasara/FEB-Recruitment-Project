from transitions import Machine
import unittest
from unittest.mock import patch

"""
What is the BMS (Battery Management System)
The primary role of a BMS is to monitor and manage the performance, safety, and longevity of a battery pack by
ensuring that it operates within safe parameters.

It should shift between battery states in order to deliver precise power and management to maximize performance.
At high speeds, failure is catastrophic so the BMS is incredibly important.
The BMS also helps manage energy usage to ensure a complete race without energy wastage.
Finally, the BMS provides live data to the car's control system in order for it to adjust and to optimize performance. 
"""

class BMS:
	"""
	Define the states of the BMS (Battery Management System) which it should transition between
	"""
	states = ["idle", "charging", "discharging", "overtemperature", "undertemperature", "undervoltage", "overvoltage", "overcurrent", "SOC Low", "SOC High", "fault"]
	#idle = default state when no charging or discharging occurs
	#charging = actively charging the battery, monitoring voltage, temperature, and current.
	#discharging = actively powering the vehicle, continuously monitoring key parameters.
	#overtemperature = engaged when battery temperature is too high, triggering cooling or shutting down operations.
	#undertemperature = activated if temperature falls below operational limits, preventing damage from cold conditions
	#undervoltage = activated when the voltage drops too low; stops discharging to protect the cells.
	#overvoltage = triggered when voltage exceeds safe limits; shuts down charging to prevent damage.
	#overcurrent = detects when current exceeds the maximum allowable level during charge or discharge.
	#fault = handles all severe faults, including simultaneous overvoltage and overtemperature conditions, requiring a reset to return to a safe state
	def __init__(self):
		# Initialize the state machine with the initial state set to 'idle'
		self.machine = Machine(model=self, states=BMS.states, initial='idle')

		#state transitions from idle to other logical states given sensor inputs
		self.machine.add_transition(trigger="start_charging", source="idle", dest="charging")
		self.machine.add_transition(trigger="start_discharging", source="idle", dest="discharging")
		self.machine.add_transition(trigger="voltage_high_warning", source="idle", dest="overvoltage")
		self.machine.add_transition(trigger="voltage_low_warning", source="idle", dest="undervoltage")
		self.machine.add_transition(trigger="temperature_high_warning", source="idle", dest="overtemperature")
		self.machine.add_transition(trigger="temperature_low_warning", source="idle", dest="undertemperature")
		self.machine.add_transition(trigger="current_high_warning", source="idle", dest="overcurrent")
		self.machine.add_transition(trigger="SOC_low_warning", source="idle", dest="SOC Low")
		self.machine.add_transition(trigger="SOC_high_warning", source="idle", dest="SOC High")
		self.machine.add_transition(trigger="start_fault", source="idle", dest="fault")

		#state transitions from charging to other logical states given sensor inputs
		self.machine.add_transition(trigger="charge_complete", source="charging", dest="idle")
		self.machine.add_transition(trigger="voltage_high_warning", source="charging", dest="overvoltage")
		self.machine.add_transition(trigger="temperature_high_warning", source="charging", dest="overtemperature")
		self.machine.add_transition(trigger="current_high_warning", source="charging", dest="overcurrent")
		self.machine.add_transition(trigger="charging_fault", source="charging", dest="fault")

		#state transitions from discharging to other logical states given sensor inputs
		self.machine.add_transition(trigger="discharging_complete", source="discharging", dest="idle")
		self.machine.add_transition(trigger="voltage_high_warning", source="discharging", dest="overvoltage")
		self.machine.add_transition(trigger="voltage_low_warning", source="discharging", dest="undervoltage")
		self.machine.add_transition(trigger="temperature_high_warning", source="discharging", dest="overtemperature")
		self.machine.add_transition(trigger="current_high_warning", source="discharging", dest="overcurrent")
		self.machine.add_transition(trigger="discharging_fault", source="discharging", dest="fault")

		#state transitions from overvoltage to other logical states given sensor inputs
		self.machine.add_transition(trigger="voltage_safe", source="overvoltage", dest="idle")
		self.machine.add_transition(trigger="start_discharging", source="overvoltage", dest="discharging")
		self.machine.add_transition(trigger="voltage_persistent_high", source="overvoltage", dest="fault")

		#state transitions from undervoltage to other logical states given sensor inputs
		self.machine.add_transition(trigger="voltage_safe", source="undervoltage", dest="idle")
		self.machine.add_transition(trigger="start_charging", source="undervoltage", dest="charging")
		self.machine.add_transition(trigger="voltage_persistent_low", source="undervoltage", dest="fault")

		#state transitions from overcurrent to other logical states given sensor inputs
		self.machine.add_transition(trigger="current_safe", source="overcurrent", dest="idle")
		self.machine.add_transition(trigger="resume_charging", source="overcurrent", dest="charging")
		self.machine.add_transition(trigger="resume_discharging", source="overcurrent", dest="discharging")
		self.machine.add_transition(trigger="current_persistent_high", source="overcurrent", dest="fault")

		#state transitions from overtemperature to other logical states given sensor inputs
		self.machine.add_transition(trigger="temperature_safe", source="overtemperature", dest="idle")
		self.machine.add_transition(trigger="resume_charging", source="overtemperature", dest="charging")
		self.machine.add_transition(trigger="resume_discharging", source="overtemperature", dest="discharging")
		self.machine.add_transition(trigger="temperature_persistent_high", source="overtemperature", dest="fault")

		#state transitions from undertemperature to other logical states given sensor inputs
		self.machine.add_transition(trigger="temperature_safe", source="undertemperature", dest="idle")
		self.machine.add_transition(trigger="resume_charging", source="undertemperature", dest="charging")
		self.machine.add_transition(trigger="temperature_persistent_low", source="undertemperature", dest="fault")

		#state transitions from SOC Low to other logical states given sensor inputs
		self.machine.add_transition(trigger="soc_safe", source="SOC Low", dest="idle")
		self.machine.add_transition(trigger="start_charging", source="SOC Low", dest="charging")
		self.machine.add_transition(trigger="soc_low_persistent", source="SOC Low", dest="fault")

		#state transitions from SOC High to other logical states given sensor inputs
		self.machine.add_transition(trigger="soc_safe", source="SOC High", dest="idle")
		self.machine.add_transition(trigger="start_discharging", source="SOC High", dest="discharging")
		self.machine.add_transition(trigger="soc_high_persistent", source="SOC High", dest="fault")

		#state transitions from fault to other logical states given sensor inputs
		self.machine.add_transition(trigger="reset_fault", source="fault", dest="idle")
"""
class TestBMS(unittest.TestCase):
    def setUp(self):
        self.bms = BMS()

    def test_initial_state(self):
        self.assertEqual(self.bms.state, 'idle')

    def test_charging_to_idle(self):
    	self.bms.start_charging()
    	self.assertEqual(self.bms.state, 'charging')
    	self.bms.charge_complete()
    	self.assertEqual(self.bms.state, 'idle')

    def test_charging_to_fault(self):
    	self.bms.start_charging()
    	self.bms.charging_fault()
    	self.assertEqual(self.bms.state, 'fault')

    def test_discharging_to_idle(self):
        self.bms.start_discharging()
        self.assertEqual(self.bms.state, 'discharging')
        self.bms.discharging_complete()
        self.assertEqual(self.bms.state, 'idle')

    def test_discharging_to_overvoltage(self):
        self.bms.start_discharging()
        self.assertEqual(self.bms.state, 'discharging')
        self.bms.voltage_high_warning()
        self.assertEqual(self.bms.state, 'overvoltage')

    def test_discharging_to_undervoltage(self):
        self.bms.start_discharging()
        self.bms.voltage_low_warning()
        self.assertEqual(self.bms.state, 'undervoltage')

    def test_discharging_to_overtemperature(self):
        self.bms.start_discharging()
        self.bms.temperature_high_warning()
        self.assertEqual(self.bms.state, 'overtemperature')

    def test_discharging_to_overcurrent(self):
        self.bms.start_discharging()
        self.bms.current_high_warning()
        self.assertEqual(self.bms.state, 'overcurrent')

    def test_overvoltage_to_idle(self):
        self.bms.voltage_high_warning()
        self.assertEqual(self.bms.state, 'overvoltage')
        self.bms.voltage_safe()
        self.assertEqual(self.bms.state, 'idle')

    def test_overvoltage_to_discharging(self):
        self.bms.voltage_high_warning()
        self.bms.start_discharging()
        self.assertEqual(self.bms.state, 'discharging')

    def test_overvoltage_to_fault(self):
        self.bms.voltage_high_warning()
        self.bms.voltage_persistent_high()
        self.assertEqual(self.bms.state, 'fault')

    def test_undervoltage_to_idle(self):
        self.bms.voltage_low_warning()
        self.assertEqual(self.bms.state, 'undervoltage')
        self.bms.voltage_safe()
        self.assertEqual(self.bms.state, 'idle')

    def test_undervoltage_to_charging(self):
        self.bms.voltage_low_warning()
        self.bms.start_charging()
        self.assertEqual(self.bms.state, 'charging')

    def test_undervoltage_to_fault(self):
        self.bms.voltage_low_warning()
        self.bms.voltage_persistent_low()
        self.assertEqual(self.bms.state, 'fault')

    def test_overcurrent_to_idle(self):
        self.bms.current_high_warning()
        self.assertEqual(self.bms.state, 'overcurrent')
        self.bms.current_safe()
        self.assertEqual(self.bms.state, 'idle')

    def test_overcurrent_to_charging(self):
        self.bms.current_high_warning()
        self.bms.resume_charging()
        self.assertEqual(self.bms.state, 'charging')

    def test_overcurrent_to_discharging(self):
        self.bms.current_high_warning()
        self.bms.resume_discharging()
        self.assertEqual(self.bms.state, 'discharging')

    def test_overcurrent_to_fault(self):
        self.bms.current_high_warning()
        self.bms.current_persistent_high()
        self.assertEqual(self.bms.state, 'fault')

    def test_overtemperature_to_idle(self):
        self.bms.temperature_high_warning()
        self.assertEqual(self.bms.state, 'overtemperature')
        self.bms.temperature_safe()
        self.assertEqual(self.bms.state, 'idle')

    def test_overtemperature_to_charging(self):
        self.bms.temperature_high_warning()
        self.bms.resume_charging()
        self.assertEqual(self.bms.state, 'charging')

    def test_overtemperature_to_discharging(self):
        self.bms.temperature_high_warning()
        self.bms.resume_discharging()
        self.assertEqual(self.bms.state, 'discharging')

    def test_overtemperature_to_fault(self):
        self.bms.temperature_high_warning()
        self.bms.temperature_persistent_high()
        self.assertEqual(self.bms.state, 'fault')

    def test_undertemperature_to_idle(self):
        self.bms.temperature_low_warning()
        self.assertEqual(self.bms.state, 'undertemperature')
        self.bms.temperature_safe()
        self.assertEqual(self.bms.state, 'idle')

    def test_undertemperature_to_charging(self):
        self.bms.temperature_low_warning()
        self.bms.resume_charging()
        self.assertEqual(self.bms.state, 'charging')

    def test_undertemperature_to_fault(self):
        self.bms.temperature_low_warning()
        self.bms.temperature_persistent_low()
        self.assertEqual(self.bms.state, 'fault')

    def test_SOC_Low_to_idle(self):
    	self.bms.SOC_low_warning()
    	self.assertEqual(self.bms.state, 'SOC Low')
    	self.bms.soc_safe()
    	self.assertEqual(self.bms.state, 'idle')

    def test_SOC_Low_to_charging(self):
    	self.bms.SOC_low_warning()
    	self.bms.start_charging()
    	self.assertEqual(self.bms.state, 'charging')

    def test_SOC_Low_to_fault(self):
    	self.bms.SOC_low_warning()
    	self.bms.soc_low_persistent()
    	self.assertEqual(self.bms.state, 'fault')

    def test_SOC_Low_to_idle(self):
    	self.bms.SOC_high_warning()
    	self.assertEqual(self.bms.state, 'SOC High')
    	self.bms.soc_safe()
    	self.assertEqual(self.bms.state, 'idle')

    def test_SOC_High_to_charging(self):
    	self.bms.SOC_high_warning()
    	self.bms.start_discharging()
    	self.assertEqual(self.bms.state, 'discharging')

    def test_SOC_High_to_fault(self):
    	self.bms.SOC_high_warning()
    	self.bms.soc_high_persistent()
    	self.assertEqual(self.bms.state, 'fault')

    def test_fault_reset(self):
        self.bms.start_fault()
        self.assertEqual(self.bms.state, 'fault')
        self.bms.reset_fault()
        self.assertEqual(self.bms.state, 'idle')

if __name__ == '__main__':
    unittest.main()
"""
file_number = input("Which text file number do you want to insert: \n")

def inside_range(val, range_min, range_max):
	if min(float(val), float(range_min))==float(range_min) and max(float(val), float(range_max))==float(range_max):
		return True
	return False

def to_idle(state):
	if state=="charging":
		return "charge_complete"
	elif state=="discharging":
		return "discharging_complete"
	elif state=="overvoltage" or state=="undervoltage":
		return "voltage_safe"
	elif state=="overcurrent":
		return "current_safe"
	elif state=="overtemperature" or state=="undertemperature":
		return "temperature_safe"
	elif state=="SOC Low" or state=="SOC High":
		return "soc_safe"
	else:
		return "reset_fault"

def file_scraper():
	bms = BMS()
	with open(f"dummy_file_{file_number}.txt", "r") as d_f:
		d_f_lines = d_f.readlines()
		now_SOC = 0
		previous_state = "idle"
		for line in d_f_lines:
			line_info = line.strip("\n").split(" ")
			now_voltage, now_current, now_temperature, now_capacity = line_info[1], line_info[2], line_info[3], line_info[4]
			charging = False
			if d_f_lines.index(line)<=len(d_f_lines)/2:
				charging = True

			delta_soc = float(now_current)/(36 * float(now_capacity))
			voltage_inside = inside_range(now_voltage, 2.50, 4.20)
			if charging:
				now_SOC+=delta_soc
				current_inside, temperature_inside, SOC_inside = inside_range(now_current, 0.00, 20.00), inside_range(now_temperature, 0.00, 45.00), inside_range(now_SOC, 0.2, 0.8)

			else:
				now_SOC-=delta_soc
				now_SOC = max(0, now_SOC)
				current_inside, temperature_inside, SOC_inside = inside_range(now_current, 0.00, 120.00), inside_range(now_temperature, -20.00, 60.00), inside_range(now_SOC, 0.2, 0.8)

			if d_f_lines.index(line)==0:
				SOC_inside = True
			outside_of_range_count = 0
			outside_of_range = ""
			inside_check_list = [voltage_inside, current_inside, temperature_inside, SOC_inside]
			for item in inside_check_list:
				if not item:
					if outside_of_range_count==1:
						outside_of_range_count+=1
						break
					if item==voltage_inside:
						outside_of_range = "voltage"
						outside_of_range_count+=1
					elif item==current_inside:
						outside_of_range = "current"
						outside_of_range_count+=1
					elif item==temperature_inside:
						outside_of_range = "temperature"
						outside_of_range_count+=1
					elif item==SOC_inside:
						outside_of_range = "SOC"
						outside_of_range_count+=1
			if outside_of_range_count>1:
				#previous => fault   (CHECKED, connect everything to idle first)
				if previous_state!="idle":
					getattr(bms, to_idle(previous_state))()
				bms.start_fault()
				previous_state = "fault"
				print(previous_state + "--------" + line)
			elif outside_of_range_count==1:
				if outside_of_range=="voltage":
					if now_voltage > 4.20:
						#previous => overvoltage (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.voltage_high_warning()
						previous_state = "overvoltage"
						print(previous_state + "--------" + line)
					else:
						#previous => undervoltage (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.voltage_low_warning()
						previous_state = "undervoltage"
						print(previous_state + "--------" + line)
				elif outside_of_range=="current":
					#previous => overcurrent (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.current_high_warning()
						previous_state = "overcurrent"
						print(previous_state + "--------" + line)
				elif outside_of_range=="temperature":
					if now_temperature<0.00 or now_temperature<-20.00:
						#previous => undertemperature (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.temperature_low_warning()
						previous_state = "undertemperature"
						print(previous_state + "--------" + line)
					else:
						#previous => overtemperature (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.temperature_high_warning()
						previous_state = "overtemperature"
						print(previous_state + "--------" + line)
				else:
					if now_SOC<0.2:
						#previous => SOC Low (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.SOC_low_warning()
						previous_state = "SOC Low"
						print(previous_state + "--------" + line)
					else:
						#previous => SOC High (CHECKED, connect everything to idle first)
						if previous_state!="idle":
							getattr(bms, to_idle(previous_state))()
						bms.SOC_high_warning()
						previous_state = "SOC High"
						print(previous_state + "--------" + line)
			else:
				if charging:
					#previous => charging (CHECKED, connect everything to idle first)
					if previous_state!="idle":
						getattr(bms, to_idle(previous_state))()
					bms.start_charging()
					previous_state = "charging"
					print(previous_state + "--------" + line)
				else:
					#previous => discharging (CHECKED, connect everything to idle first)
					if previous_state!="idle":
						getattr(bms, to_idle(previous_state))()
					bms.start_discharging()
					previous_state = "discharging"
					print(previous_state + "--------" + line)

file_scraper()