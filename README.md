
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

Background
----------

These are real-world problems. Every member of a group of students
needed to meet every other student for a short peer-to-peer discussion.
The organizational problem appeared trivial at first, but it proved
difficult in both practice and theory.

If N is even, then N students should be able to meet each other in N - 1 rounds.
However, if the meetings happen in the wrong sequence, then they can delay
later meetings, and it takes more than N - 1 rounds for everyone to meet.
In reality, there were students sitting out before half of the meetings had
taken place. These students had already met each other.

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

Algorithms
----------

My investigation into possible algorithms for this problem is in
another document: [algorithms.md](algorithms.md).

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


