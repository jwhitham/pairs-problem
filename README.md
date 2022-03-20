
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
stands out as a representation of what I had called the "pairs problem".

The goal within each round is to find a
[maximum cardinality matching](https://en.wikipedia.org/wiki/Maximum_cardinality_matching)
on an arbitrary graph. In the first round of Problem 1, anyone can meet anyone, so the
graph consists of N vertices (representing N students) and N(N-1) edges linking
every vertex to every other vertex. In Problem 2, and in subsequent rounds of
Problem 1, some edges are removed, since some students already met.
The [blossom algorithm](https://en.wikipedia.org/wiki/Blossom_algorithm) provides a
solution; more efficient but more complex algorithms have since been discovered
by researchers. My own algorithm is much less efficient than any of these, becoming
completely ineffective for large numbers of students due to high time complexity.

Solver
------

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


