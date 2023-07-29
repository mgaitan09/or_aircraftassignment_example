from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, value, LpStatus
import numpy as np
import math
import itertools

# Flight Data
flight_ids = [1, 2, 3]
flight_durations = [2, 3, 2.5]
flight_costs = [[10, 15, 20], [12, 18, 22], [11, 14, 17]]

# Convert flight durations to integer by rounding up to the nearest hour
flight_durations = [math.ceil(i) for i in flight_durations]

# Aircraft Data
aircraft_ids = [1, 2, 3]
maintenance_schedules = [[0, 0, 1, 1, 1, 0, 0], [1, 0, 0, 0, 1, 1, 0], [0, 1, 1, 0, 0,0, 1]]

# Initiate the problem
problem = LpProblem("Flight_Scheduling", LpMinimize)

# Decision variable dictionary {Flight, Aircraft, Time}
var_dict = LpVariable.dicts('F_A_T', itertools.product(flight_ids, aircraft_ids, range(len(maintenance_schedules[0]))), cat=LpBinary)

# Objective function
problem += lpSum([var_dict[(f, a, t)] * flight_costs[f - 1][a - 1] for f, a, t in var_dict])

# Constraints
# Each flight is assigned to exactly one aircraft at a specific start time
for f in flight_ids:
    problem += lpSum([var_dict[(f, a, t)] for a in aircraft_ids for t in range(len(maintenance_schedules[0]))]) == 1

# Each aircraft is assigned to at most one flight at a time and is not in maintenance
for a in aircraft_ids:
    for t in range(len(maintenance_schedules[0])):
        # No more than one flight at a time
        problem += lpSum([var_dict[(f, a, t2)] for f in flight_ids for t2 in range(max(0, t - flight_durations[f - 1] + 1), min(t + 1, len(maintenance_schedules[0])))]) <= 1
        # No flights during maintenance
        if maintenance_schedules[a - 1][t] == 1:
            problem += lpSum([var_dict[(f, a, t2)] for f in flight_ids for t2 in range(max(0, t - flight_durations[f - 1] + 1), min(t + 1, len(maintenance_schedules[0])))]) == 0

# Flights can't start if there aren't enough hours left for it to finish
for f in flight_ids:
    for a in aircraft_ids:
        for t in range(len(maintenance_schedules[0]) - flight_durations[f - 1] + 1, len(maintenance_schedules[0])):
            problem += var_dict[(f, a, t)] == 0

# Solve the problem
problem.solve()

# Check status
print("Status:", LpStatus[problem.status])

# Optimal Solution
print("Optimal Solution:")
for f, a, t in var_dict:
    if value(var_dict[(f, a, t)]) == 1:
        print(f"Flight {f} is assigned to Aircraft {a}, starts at time {t} and ends at time {t + flight_durations[f - 1]}")

# Minimal Cost
print("Minimal cost:", value(problem.objective))