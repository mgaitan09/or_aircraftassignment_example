from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, value, LpStatus
import numpy as np
import math
import itertools

# Flight Data
flight_ids = [1, 2, 3, 4 , 5]
flight_durations = [2, 3, 2.5, 2, 1.5]
flight_costs = [
    [10, 15, 20], 
    [12, 18, 22], 
    [11, 14, 17], 
    [9, 13, 19], 
    [8, 16, 21]
]

# Convert flight durations to integer by rounding up to the nearest hour
flight_durations = [math.ceil(i) for i in flight_durations]

# Aircraft Data
aircraft_ids = [1, 2, 3]

# The length of schedule, which will be shared between flights and maintenance
schedule_length = 12

# Initiate the problem
problem = LpProblem("Flight_Scheduling", LpMinimize)

# Decision variable dictionary {Flight, Aircraft, Time}
var_dict = LpVariable.dicts('F_A_T', itertools.product(flight_ids, aircraft_ids, range(schedule_length)), cat=LpBinary)

# Decision variable dictionary {Aircraft, Time} for maintenance
maintenance_dict = LpVariable.dicts('M_A_T', itertools.product(aircraft_ids, range(schedule_length)), cat=LpBinary)

# Objective function
problem += lpSum([var_dict[(f, a, t)] * flight_costs[f - 1][a - 1] for f, a, t in var_dict])

# Constraints
# Each flight is assigned to exactly one aircraft at a specific start time
for f in flight_ids:
    problem += lpSum([var_dict[(f, a, t)] for a in aircraft_ids for t in range(schedule_length)]) == 1

# Each aircraft is assigned to at most one flight at a time and is not in maintenance
for a in aircraft_ids:
    for t in range(schedule_length):
        # No more than one flight at a time
        problem += lpSum([var_dict[(f, a, t2)] for f in flight_ids for t2 in range(max(0, t - flight_durations[f - 1] + 1), min(t + 1, schedule_length))]) + maintenance_dict[a, t] <= 1

# Flights can't start if there aren't enough hours left for it to finish
for f in flight_ids:
    for a in aircraft_ids:
        for t in range(schedule_length - flight_durations[f - 1] + 1, schedule_length):
            problem += var_dict[(f, a, t)] == 0

# Maintenance requirement
for a in aircraft_ids:
    problem += lpSum([maintenance_dict[a, t] for t in range(schedule_length)]) == 4  # Minimum 3 hours maintenance

# Solve the problem
problem.solve()

# Check status
print("Status:", LpStatus[problem.status])

# Optimal Solution
print("Optimal Solution:")
for f, a, t in var_dict:
    if value(var_dict[(f, a, t)]) == 1:
        print(f"Flight {f} is assigned to Aircraft {a}, starts at time {t} and ends at time {t + flight_durations[f - 1]}")

for a, t in maintenance_dict:
    if value(maintenance_dict[(a, t)]) == 1:
        print(f"Aircraft {a} is under maintenance at time {t}")

# Minimal Cost
print("Minimal cost:", value(problem.objective))

# Optimal Solution
print("Flight Assignments:")
for f, a, t in var_dict:
    if value(var_dict[(f, a, t)]) == 1:
        print(f"Flight {f} is assigned to Aircraft {a}, starts at time {t} and ends at time {t + flight_durations[f - 1]}")

print("\nMaintenance Schedules:")
for a in aircraft_ids:
    aircraft_maintenance = [int(value(maintenance_dict[(a, t)])) for t in range(schedule_length)]
    print(f"Aircraft {a} Maintenance Schedule: {aircraft_maintenance}")

