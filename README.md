## Problem: Airline Scheduling with Aircraft Assignment and Maintenance

You are tasked with creating an optimal schedule for a set of flights considering aircraft assignment
and maintenance constraints. 

It should ensure that: 
- each flight is assigned to exactly one aircraft.
- each aircraft is assigned to at most one flight at a time
- the number of aircraft in maintenance at any given time is limited
- the maintenance schedule is consistent
- each flight departs exactly once
- the flight duration is consistent with the assigned aircraft
- conflicts between aircraft assignments and maintenance are avoided. 

##### The goal is to minimize the total cost of aircraft assignments while ensuring operational feasibility and efficiency.

### Inputs:

##### Flight Data section 
###### Lists the flights with their respective flight IDs, durations, and the cost of assigning each aircraft to the flight. 


| Flight ID | Flight Duration (hours) | Aircraft Assignment Costs (per aircraft in order |
| -- | --| -- |
| 1 | 2 | 10, 15, 20 |
| 2 | 3 | 12, 18, 22 |
| 3 | 2.5 | 11, 14, 17 |

##### The Aircraft Data section
###### Lists the aircraft with their respective aircraft IDs and maintenance schedules. 
The maintenance schedule is represented as a binary sequence where '1' indicates the aircraft is in maintenance during that time period, and '0' indicates it is available for assignment.

| Aircraft ID | Maintenance Schedule (hours) |
| ----------- | --------------------         |
| 1           | 0, 0, 1, 1, 1, 0, ...        |
| 2           | 1, 0, 0, 1, 1, 1, ...        |
| 3           | 0, 1, 1, 0, 1, 1, ...        |


## Questions:

#### Question 1: Formulate a mixed-integer linear program (MILP).
(Hint): You can make assumptions about the constraints and objective function for this problem,
but you need to explain them clearly.

#### Question 2: We want to ensure that if an aircraft is in maintenance during a particular time period,

it cannot be assigned to any flight during that time period. Modify/Add new constraints to MILP
in Question 1

#### Question 3: What if we have some aircrafts need to be repaired in certain fixed periods.
Modify/Add new constraints to MILP in Question 1-2.



## Answers:

###### All my answers will have 3 sections. Theory, Code and Results.


### Q1 - Formulation of the MILP Problem:
###### This formulation is seen in the 'base.py'file in the [shared repo](https://github.com/mgaitan09/or_aircraftassignment_example/tree/main).
###### This formulation can be seen on Q1 Code cell in the [shared Google Colab Notebook](https://colab.research.google.com/drive/1b7WfbjD0ZU4Lu-kXtqh198z_w7ukB4OF?usp=sharing)

#### Decision Variables:

Even though we need to have in mind that the objective is to minimize cost of assigning aircrafts, we need to have a variable that represents the decision.

In This case the binary (0 or 1) variable:

`x[f, a, t]`, it means that flight `f` is 1 if assigned or 0 if not assigned to aircraft `a` at time `t`.

We will create a second decision variable, not to be used on the objective function but to include a constraint regarding total maintenances at the same time window:

`m[a, t]`, it tracks if aircraft `a` is assigned a maintenance at time `t`.

Maximum Maintenance Capacity is a variable that will be an input for how many maintenances assigned I can have per time slot.


#### Objective Function:

We know we want to Minimize the Cost of assigning Flights while still fulfilling operational restrictions (maintenance, flight consistency, etc).

Mathematically, it can be expressed as:

min ∑f ∑a ∑t (x[f, a, t] * c[f, a])

So minimize the sum of cost of all aircraft assigments for all flights at all time segments.


#### Constraints:


##### 1. Flight Assignment Constraints:
Each flight must be assigned to exactly one aircraft at a specific start time.

This constraint ensures that every flight is assigned to one aircraft at a specific start time.

##### ∑a ∑t x[f, a, t] = 1 for all f ∈ F


##### 2. Aircraft Utilization Constraints:

Each aircraft is assigned to at most one flight at a time, and is not in maintenance.
This constraint ensures that an aircraft cannot be assigned to more than one flight at a time and can not be assigned to a flight when it is scheduled for maintenance.

##### x[f, a, t] = 0 for all f ∈ F, a ∈ A, t > T - d[f]

where:
t ranges from max(0, t - d[f] + 1) to min(t + 1, T) 
and
d[f] is the duration of flight f and T is the total time available.

Also, if maintenance is scheduled for aircraft at time t we ensure that:

##### ∑f ∑t' x[f, a, t'] = 0

meaning no maintenance can be taking place at the same time a flight is taking place.

##### 3. Flight Duration Constraints:
A flight cannot be scheduled if there are not enough hours left in the day for it to be completed.
This constraint ensures that a flight is not scheduled such that it cannot be completed before the end of the day.

##### 4. Maintenance Schedule Capacity and Consistency:

Each aircraft can't be both in maintenance and not in maintenance at the same time. This constraint ensures that the `m[a, t]` variable matches the maintenance schedule.

∑t `m[a, t]` = maintenance_schedule for aircraft `a` at time `t` for all a ∈ Aircraft_IDs

Each time step should have at most "Maintenance Capacity" aircraft in maintenance. This constraint ensures that there are not too many aircraft in maintenance at the same time.

∑a `m[a, t]` <= Maximum Maintenance Capacity for all t ∈ Time

#### Input:

We need to provide the following variable in our python implementation:

flight_ids = [1, 2, 3]

flight_durations = [2, 1, 3]

flight_costs = [[10, 15, 20], [12, 18, 22], [11, 14, 17]]

aircraft_ids = [1, 2, 3]

maintenance_schedules = [[0, 0, 1, 1, 1, 0, 0], [1, 0, 1, 0, 1, 1, 0], [0, 1, 1, 0, 0, 0, 1]]
read like this:
[[aircraft1 maintenance schedule],[aircraft 2 maintenance schedule], [aircraft 3 maintenance schedule]]

in this case we have 7 time slots.

### Q1 code:

``` python
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, value, LpStatus
import numpy as np
import math
import itertools

# Flight Data
flight_ids = [1, 2, 3]
flight_durations = [2, 1, 3]
flight_costs = [[10, 15, 20], [12, 18, 22], [11, 14, 17]]

# Convert flight durations to integer by rounding up to the nearest hour
flight_durations = [math.ceil(i) for i in flight_durations]

# Aircraft Data
aircraft_ids = [1, 2, 3]
maintenance_schedules = [[0, 0, 1, 1, 1, 0, 0], [1, 0, 1, 0, 1, 1, 0], [0, 1, 1, 0, 0, 0, 1]]

# Initiate the problem
problem = LpProblem("Flight_Scheduling", LpMinimize)

# Decision variable dictionary {Flight, Aircraft, Time}
var_dict = LpVariable.dicts('F_A_T', itertools.product(flight_ids, aircraft_ids, range(len(maintenance_schedules[0]))), cat=LpBinary)

# Maintenance variable dictionary {Aircraft, Time}
maintenance_var_dict = LpVariable.dicts('M_A_T', itertools.product(aircraft_ids, range(len(maintenance_schedules[0]))), cat=LpBinary)

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
        problem += lpSum([var_dict[(f, a, t2)] for f in flight_ids for t2 in range(max(0, t - flight_durations[f - 1] + 1), min(t + 1, len(maintenance_schedules[0])))]) <= (1 - maintenance_var_dict[(a, t)])

# Flights can't start if there aren't enough hours left for it to finish
for f in flight_ids:
    for a in aircraft_ids:
        for t in range(len(maintenance_schedules[0]) - flight_durations[f - 1], len(maintenance_schedules[0])):
            problem += var_dict[(f, a, t)] == 0

# Each aircraft can't be both in maintenance and not in maintenance at the same time
for a in aircraft_ids:
    for t in range(len(maintenance_schedules[0])):
        problem += maintenance_var_dict[(a, t)] == maintenance_schedules[a - 1][t]

# Maximum number of simultaneous maintenance
max_maintenance = 3  # change this to your maximum allowed maintenance

# Each time step should have at most max_maintenance in maintenance
for t in range(len(maintenance_schedules[0])):
    problem += lpSum([maintenance_var_dict[(a, t)] for a in aircraft_ids]) <= max_maintenance

# Print the time slots when maintenance constraint is violated
for t in range(len(maintenance_schedules[0])):
    total_maintenance = sum([maintenance_schedules[a - 1][t] for a in aircraft_ids])
    if total_maintenance > max_maintenance:
        print(f"Time slot {t} has {total_maintenance} maintenance sessions which exceed the limit {max_maintenance}")

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

```

### Q2 and Q3 both refer to complying with maintenance schedule
##### Q2. "ensure that if an aircraft is in maintenance during a particular time period""
##### Q3. "What if we have some aircrafts need to be repaired in certain fixed periods.""

##### Answer: These constraints are covered in the Answer 1 since I am using the Maintenance Schedule as a constraint for the assignment of flights.

In my example code given:
```
flight_ids = [1, 2, 3]
flight_durations = [2, 1, 3]
flight_costs = [[10, 15, 20], [12, 18, 22], [11, 14, 17]]
aircraft_ids = [1, 2, 3]
maintenance_schedules = [[0, 0, 1, 1, 1, 0, 0], [1, 0, 1, 0, 1, 1, 0], [0, 1, 1, 0, 0, 0, 1]]
```
The Code will provide this solution:
```
Status: Optimal
Optimal Solution:
Flight 1 is assigned to Aircraft 1, starts at time 0 and ends at time 2
Flight 2 is assigned to Aircraft 1, starts at time 5 and ends at time 6
Flight 3 is assigned to Aircraft 3, starts at time 3 and ends at time 6
```


## Extra Credit:

### I thought this problem could be improved by letting the solver not only assign flights *but also assign maintenance* according to a minimum hours necessary.

###### In order to do this, we do not provide a maintenance schedule but instead we add a new constraint and provide this input (can be changed according to the scenario):
```
flight_ids = [1, 2, 3, 4 , 5]
flight_durations = [2, 3, 2.5, 2, 1.5]
flight_costs = [
    [10, 15, 20], 
    [12, 18, 22], 
    [11, 14, 17], 
    [9, 13, 19], 
    [8, 16, 21]
]
aircraft_ids = [1, 2, 3]
# The length of schedule, which will be shared between flights and maintenance
schedule_length = 12
```

#### New Maintenance Requirement:

Each aircraft must undergo a minimum amount of maintenance.

This constraint ensures that each aircraft is allocated at least a specified amount of maintenance time.

∑t m[a, t] = M for all a ∈ A, where M is the minimum maintenance time.

For this specific example, I didn't make the hours contiguous, but it's possible.

Example Extra Credit Code:

``` python
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
    problem += lpSum([maintenance_dict[a, t] for t in range(schedule_length)]) == 3  # Minimum 3 hours maintenance

# Maximum maintenance capacity
max_maintenance_capacity = 2

# Each time step should have at most max_maintenance in maintenance
for t in range(schedule_length):
    problem += lpSum([maintenance_dict[(a, t)] for a in aircraft_ids]) <= max_maintenance_capacity



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


```


### Please refer to the [shared Google Colab](https://colab.research.google.com/drive/1b7WfbjD0ZU4Lu-kXtqh198z_w7ukB4OF?usp=sharing) for runnable versions of this code.