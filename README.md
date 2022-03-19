
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

Notes
-----

For problem 1, if there are N students, and N is an even number, then the
optimal number of rounds is N - 1.

If N is an odd number, then the optimal number of rounds is N. In
this case, one student will have to take a break during each round
(meeting nobody).


Background
----------

This is a real-world problem from an actual class. At first it
seems quite trivial, but actually it is not easy for a large class
to organize itself optimally, and after some rounds there will
probably be some students sitting out.

Even for the simpler Problem 1, I could not think of any simple rule
which could be followed by the students in order to organize themselves
optimally.

I also could not relate this problem to any of the CS problems
that I knew of. It's reminiscent of some well-known problems, but
it involves a set of people and graph-like relationships between them,
and many CS problems are like that. Perhaps you recognize it? Perhaps
there is already a well-known textbook solution?

In its current form the program can easily support classes of around
20 students but does not scale to support many more. I am interested
in better algorithms which can solve it more quickly. Please send me an
email if you recognize the problem and know what it is called.


Solver
------

The core of the solver is in solve.py. This works from an abstract
representation of the problem (problem.py) and is tested by unit
tests in test.py. The problem can be represented in JSON form
or as a spreadsheet. The spreadsheet form is intended to be
directly viewed and edited by users.

capture.py uses the Google Docs API to access the spreadsheet,
which should have two pages: Input and Output. Input contains
a table of people marked up with "MET", while Output is updated
by the program to contain the finished schedule. Here is a partial
example:

![screenshot](/sample.png)

The Google spreadsheet requires the Google
client library to be installed. I based my work on the
[Python quickstart guide](https://developers.google.com/sheets/api/quickstart/python)
using authorization credentials for a desktop application.

Sample data set
---------------

test\_ysj2.json is a sample real-world data set for a class of
19 students after one session already took place. In this first
session, one student ("G2") was absent due to illness. The other
18 formed a horseshoe double ring in which 9 were on the inside
and 9 were on the outside. The students rotated after each round,
but after 9 rounds, discovered that they had returned to their
original pairings. They attempted to pair up by hand, but this
left some students with nothing to do, because pairing is
not a trivial problem. The data set represents the state of 
the problem at the beginning of the second session,
where most students still need to meet 8 or 9 others,
and G2 must meet 18 others.

test.py has code to generate arbitrary-sized variants of this
problem from pseudorandom data.

