
Pairs problem
=============

_Scenario_: A group of students are taking a class at a university,
and the class includes some groupwork exercises.
One of these exercises involves one-to-one meetings in which the
students carry out some task together.

In order to pass the course, each student must meet each other
student _exactly once_. An organizer wishes to
create a _schedule_ which lists the student meetings.
To maximize efficiency, this schedule should be as short as possible.

Each meeting takes ten minutes, so the meeting schedule is divided
into ten minute _rounds_. During each round, meetings
take place simultaneously. Each student can only be in one
meeting, and each meeting consists of only two students.

Problem
-------

_Problem 1_: Generate a schedule consisting of a minimum number
of rounds, in which every student meets every other student
exactly once. For problem 1, the input is a list of students.

_Problem 2_: Solve Problem 1 but with the additional constraint
that some students have already met. For problem 2, the input
is a list of students, plus a list of pairs that have already met.

Examples
--------

Four students: Alice, Bob, Charlie and Donna.

* In round 1, Alice meets Bob, and Charlie meets Donna.
* In round 2, Alice meets Charlie, and Bob meets Donna.
* In round 3, Alice meets Donna, and Bob meets Charlie.

At the end of round 3, all the students have met each other exactly once.

Five students: Eve, Frank, George, Harriet and Irma.
Frank and George already met.

* In round 1, Eve meets Harriet, Frank meets Irma. George sits out.
* In round 2, Eve meets Irma, George meets Harriet. Frank sits out.
* In round 3, Eve meets Frank, George meets Irma. Harriet sits out.
* In round 4, Eve meets George, Frank meets Harriet. Irma sits out.
* In round 5, Harriet meets Irma. Everybody else goes home.

At the end of round 5, all the students have met each other exactly once.

Background
----------

This is a real-world problem from an actual class. At first it
seems quite trivial, but actually it is not easy for a large class
to organize itself optimally, and after some rounds there will
probably be some students sitting out.

I thought this could be a well-known CS problem, but I didn't know what
to search for, having no name for it. However, you can also search
for numbers. When I worked out the number of possible pairings for the first round
for 2, 4, 6, 8 students and so on, I found the sequence 1, 3, 15,
105, 945, 10395, 135135... Searching for this sequence reveals it is
the [double factorial](https://en.wikipedia.org/wiki/Double_factorial)
sequence and the
[chord diagram](https://commons.wikimedia.org/wiki/File:Chord_diagrams_K6_matchings.svg)
at the top of the Wikipedia page immediately
stands out as a representation of possible pairings for each round.

Within each round, the first goal is to find pairings between students who
have not already met. This is "[maximum cardinality
matching](https://en.wikipedia.org/wiki/Maximum_cardinality_matching)"
on an _arbitrary_ graph: arbitrary as opposed to special cases such as a
_bipartite_ graph where the students have been divided into two groups.
This problem can be solved efficiently by
the [blossom algorithm](https://en.wikipedia.org/wiki/Blossom_algorithm) and
various others.

However, there is a second and equally important goal, which is to find
pairings so that the remaining number of rounds is minimised. Not all pairings
do this. For example, revisiting Eve, Frank, George, Harriet and Irma, consider
the following pairings:

* Round 1: Eve + George, Frank + Harriet, Irma sits out
* Round 2: Frank + Irma, Eve + Harriet, George sits out
* Round 3: Frank + George, Eve + Irma, Harriet sits out
* Round 4: Eve + Frank, George + Irma, Harriet sits out again

All of these pairings are valid, as nobody meets the same person twice,
and nobody meets two others at the same time. However, it will now require
two more rounds for everyone to meet, as poor Harriet has still not met George or
Irma. In total, six rounds are required, though we already know that
five are possible. A different choice in round 4 will not help, as there is no other
way to hold two meetings at that time. 

This example shows that the pairs problem is more difficult than
maximum cardinality matching, because of the need to minimise the number
of rounds. It is not enough to simply find a perfect matching: we must also
find one that will allow further perfect matchings in subsequent rounds.

My algorithm
------------

The algorithm used in my solver is the one you might use when trying to solve the
problem on paper. Consider your students as letters, A, B, C, D etc., and a pair
of students is a pair of letters, e.g. "AB", in which the first letter must always be smaller
than the second.

If there are an odd number of students, introduce "nobody" as an additional person
to be paired, assigned the letter "X".

Write a table of rounds and pairings.
Always write the smallest pair that can fit (using dictionary order).

For example:

     round 1:  AB CD EX
     round 2:  AC BE DX
     round 3:  AD BX CE
     round 4:  AE BD CX
     round 5:  AX BC DE

In round 2, after you write "AC BD", you find you have to backtrack, because while "BD" is
valid, the only possibility for the final pair is "EX", which appeared in round 1.
"BE" must be picked instead.

This backtracking leads to the computational inefficiency of the solver (probably exponential), but
when combined with the need to choose the smallest possible pairs that fill each
round, it also appears to find an optimal allocation for all rounds (solving Problem 1).
However, there is no proof of this. The search for a counter-example is difficult because
the algorithm's time complexity is bad, and it's not possible to test large numbers of students.

Implementation
--------------

The core of the solver is in solve.py. This works from an abstract
representation of the problem (problem.py) and is tested by unit
tests in test.py. The problem can be represented in JSON form
or as a spreadsheet. The spreadsheet form is intended to be
directly viewed and edited by users.

Spreadsheet
-----------

The spreadsheet is stored in Google Docs. There are two pages,
Input and Output. Input contains a table of people, listed both
across (cells C1, D1, E1..) and down (cells A2, A3, A4...). These
two lists must match, i.e. A2 = C1, A3 = D1, etc.

If a cell corresponding to two names contains a "truthy" value
such as "MET", "TRUE", or "1", then the algorithm considers those
people to have already met.

Column B allows each person to be easily removed from the problem,
e.g. if they are absent. A "falsey" value in this column will
exclude that person.

[Here is an example](https://docs.google.com/spreadsheets/d/1RUksPozO0sZPyPnlRhDgmgyIMZz3gNYWlNSmTYpr2mo/edit?usp=sharing).

Input:

![input](/sample-input.png)

Output:

![output](/sample-output.png)

The Google spreadsheet requires the Google
client library to be installed. I based capture.py on Google's
[Python quickstart guide](https://developers.google.com/sheets/api/quickstart/python)
using authorization credentials for a desktop application.


Improved algorithms
===================

I am unhappy with solve.py for various reasons:

* The algorithm is not efficient (exponential backtracking is needed)
* I don't know if it really produces an optimal solution for any N.

I decided to look into the problems further.

Special case of Problem 1: Powers of Two
----------------------------------------

Problem 1 is a special case of Problem 2 in which nobody has already met. Problem 1 has a further
special case in which the number of students is a power of two. If N is a power
of two, then it is possible to generate the pairings by dividing the students into groups in a
recursive process.

A group of size N is divided into two halves (odd and even). Pairs are formed between the two
halves. Then, one half is _rotated_, such that each student is meeting a new person. After N/2 rotations,
all of the students are meeting someone that they already talked to. At this point, a _crossover_
takes place, in which half of the students swap halves, and the resulting group is divided into two
groups of size N/2. The process repeats recursively until no further subdivisions are possible (i.e. N = 2).

For example:

    (initial group, N = 8)
      round 1: AB CD EF GH
    (rotate)
      round 2: AD CF EH BG 
    (rotate)
      round 3: AF CH BE DG 
    (rotate)
      round 4: AH BC DE FG 
    (rotate, crossover, subdivide into two groups with N = 4)
      round 5: AC EG BD FH 
    (rotate both groups)
      round 6: AG CE BH DF 
    (rotate both groups, crossover, subdivide into four groups with N = 2)
      round 7: AE BF CG DH 
    (rotate, crossover, no further divisions are possible, stop)

For details of this algorithm, see rot.py. I found that it produces optimal pairings, with a total
of N-1 rounds being required. It is also efficient, requiring only linear-time operations during each
round. It never searches for solutions, instead generating them using _rotate_, _crossover_ and
_subdivide_ steps. However, it can only be used if N is a power of 2, since it relies on being able to
divide any group exactly in half.

General Problem 1 by search
---------------------------

I experimented with various ways to improve the efficiency of the algorithm for general values of N.
Assuming that it is necessary to search, the best solution would be to make the correct pairing
choices on the first attempt, without any need to backtrack.

The original algorithm (solve.py) searches for pairings based only on student numbers, so it
sorts the possible pairs using the following priority function, and tries the smallest
value first:

    priority(S1, S2) = (min(S1, S2), max(S1, S2))

In triangle.py, I tried evaluating the _availability_ of each student, defined as how many other students they
can still meet. I prioritised possible pairs using this availablity, with the least available student's
availability appearing first in the sort key, then the other student's availability, and then the
pair itself (smallest student number, then largest)):

    priority1(S1, S2) = (min(availability(S1), availability(S2)),
                         max(availability(S1), availability(S2)),
                         min(S1, S2),
                         max(S1, S2))

Always choosing the smallest priority1 pair will lead to an optimal solution to Problem 1, without
backtracking, for all N up to 18. 

However, with N=20, the algorithm makes an incorrect choice in some early round, leading to an impossible
situation in the 18th round. In the 18th round, each of the students must still meet two others. If
I draw a graph of who can meet, I find that the students form two chains, one containing 9 people,
the other containing 11:

    A - S - F - M - L - D - Q - E - T - A
    B - I - G - N - K - H - R - J - O - C - P - B

As these chains have odd-numbered lengths, it is impossible for all students
to pair up. An optimal allocation can't be made for that round, two people will be
left out, and since the algorithm cannot backtrack to an earlier round, it fails.
Problem 1 is not solved.

I am unconvinced that searching for solutions is a useful approach, given that (1) it is not
necessary when N is a power of 2, and (2) that searching seems to always require backtracking
for sufficiently large N, no matter what criteria is used to guide choices.


General Problem 1 by induction
------------------------------

If we have an optimal solution for N people, can it be modified to produce an optimal solution
for N+2 people? This would involve adding two more rounds and appropriately merging the new pair
into the existing list.

