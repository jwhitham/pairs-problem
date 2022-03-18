
import typing

MAX_NAMES = 24

Cell = typing.Tuple[int, int]

class CaptureError(Exception):
    pass

class Person:
    def __init__(self, name: str, is_present: bool) -> None:
        self.name = name
        self.is_present = is_present
        self.already_met: typing.List[Person] = []
        self.schedule: typing.List[Person] = []
    
    def add_to_schedule(self, round_number: int, other: "Person") -> None:
        while len(self.schedule) <= round_number:
            self.schedule.append(NOBODY)
        self.schedule[round_number] = other

NOBODY = Person("*nobody*", False)

class Spreadsheet:
    def __init__(self, values: typing.List[typing.List[str]] = []) -> None:
        self.values: typing.List[typing.List[str]] = values

    def __getitem__(self, cell: Cell) -> str:
        (x, y) = cell
        if not (0 <= y < len(self.values)):
            return ""

        row = self.values[y]
        if not (0 <= x < len(row)):
            return ""

        return row[x]

    def __setitem__(self, cell: Cell, value: str) -> None:
        (x, y) = cell
        while len(self.values) <= y:
            self.values.append([])

        row = self.values[y]
        while len(row) <= x:
            row.append("")

        row[x] = value

class Problem:
    def __init__(self) -> None:
        self.people: typing.List[Person] = []

    def reset(self) -> None:
        for p in self.people:
            p.schedule.clear()

    def validate_problem(self) -> bool:
        return self.validate(problem_only=True)

    def validate_solution(self) -> bool:
        return self.validate(problem_only=False)

    def validate(self, problem_only: bool) -> bool:
        all_people = set(self.people)
        names_seen: typing.Set[str] = set()

        # The people list elements must be unique
        if len(all_people) != len(self.people):
            return False

        # Check each person individually
        for p1 in self.people:
            met = set()
            met.add(p1)
            if p1 is NOBODY:
                return False

            for p2 in p1.already_met:
                if not (p2 in all_people):
                    # Already met someone we don't know
                    return False
                if p2 in met:
                    # Already met someone twice
                    return False
                met.add(p2)

            for p2 in p1.schedule:
                if p2 is NOBODY:
                    continue
                if (not p1.is_present) or (not p2.is_present):
                    # Met someone who isn't present
                    return False
                if not (p2 in all_people):
                    # Met someone we don't know
                    return False
                if p2 in met:
                    # Met someone twice
                    return False
                met.add(p2)

            # Each person should have met all other people once
            if (met != all_people) and not problem_only:
                return False

            # Person must have a valid name
            if (p1.name == "") or (p1.name == NOBODY.name) or (p1.name in names_seen):
                return False

            names_seen.add(p1.name)

        # Check consistent schedule length
        size = 0
        for p1 in self.people:
            if p1.is_present:
                size = len(p1.schedule)
                break

        for p1 in self.people:
            if p1.is_present:
                if size != len(p1.schedule):
                    # Schedule size differs
                    return False
            else:
                if 0 != len(p1.schedule):
                    # Schedule size should be 0 when not present
                    return False

        # Check consistent schedule relationships
        for p1 in self.people:
            for (i, p2) in enumerate(p1.schedule):
                if p2 is NOBODY:
                    continue
                if p2.schedule[i] != p1:
                    # p2 doesn't meet p1 at time i - schedule doesn't match
                    return False

        # Check consistent already_met relationships
        for p1 in self.people:
            for p2 in p1.already_met:
                if not (p1 in p2.already_met):
                    # p1 met p2, but p2 didn't meet p1?
                    return False

        return True


    @staticmethod
    def from_spreadsheet(values: Spreadsheet,
                    cell_name_fn: typing.Callable[[Cell], str]) -> "Problem":
        # Capture names (and check for consistency)
        row_names = set()
        for i in range(MAX_NAMES):
            name = values[(0, i + 1)]

            if name.lower() in row_names:
                raise CaptureError("Invalid name in cell {}: duplicate '{}'".format(
                            cell_name_fn((0, i + 1)), name))

            if values[(i + 2, 0)] != name:
                raise CaptureError("Invalid name '{}' in cell {} "
                    "- need this name to appear in cell {} too".format(
                            name, cell_name_fn((i + 2, 0)),
                            cell_name_fn((0, i + 1))))
            if name == "":
                break

            row_names.add(name.lower())
        num_names = len(row_names)

        # Read presence values and create records for people
        self = Problem()
        people = self.people
        for y in range(num_names):
            people.append(Person(name=values[(0, y + 1)],
                            is_present=is_truthy(values[(1, y + 1)])))

        # Find out who already talked to whom
        for y in range(num_names):
            for x in range(num_names):
                if x != y:
                    v = values[(2 + x, 1 + y)]
                    if is_truthy(v):
                        people[x].already_met.append(people[y])
                        people[y].already_met.append(people[x])
                    elif v.startswith("round "):
                        try:
                            r = int(v.split()[-1])
                            if (r < 1) or (r > num_names):
                                raise ValueError()
                        except ValueError:
                            raise CaptureError(
                                "Invalid round number '{}' in cell {}".format(
                                        v, cell_name_fn((2 + x, 1 + y)))) from None
                        people[x].add_to_schedule(r - 1, people[y])
                        people[y].add_to_schedule(r - 1, people[x])

        # Normalise schedule length for all people who are present
        size = 0
        for p1 in self.people:
            if p1.is_present:
                size = max(size, len(p1.schedule))

        for p1 in self.people:
            if p1.is_present and len(p1.schedule) < size:
                p1.add_to_schedule(size - 1, NOBODY)

        return self

    def to_spreadsheet(self) -> Spreadsheet:
        values = Spreadsheet()
        values[(1, 0)] = "IS PRESENT"
        values[(0, 0)] = ""
        number: typing.Dict[str, int] = dict()

        # Headers, presence
        for (i, p1) in enumerate(self.people):
            values[(2 + i, 0)] = p1.name
            values[(0, 1 + i)] = p1.name
            values[(1, 1 + i)] = str(p1.is_present).upper()
            number[p1.name] = i

        # Initial state is unmet
        for i in range(len(self.people)):
            for j in range(len(self.people)):
                values[(2 + j, 1 + i)] = "unmet"

        # ...but nobody has met themselves
        for i in range(len(self.people)):
            values[(2 + i, 1 + i)] = "-"

        # Fill in "already met"
        for p1 in self.people:
            a = number[p1.name]
            for p2 in p1.already_met:
                b = number[p2.name]
                values[(2 + a, 1 + b)] = "met"

        # Fill in round numbers if available
        for p1 in self.people:
            a = number[p1.name]
            for (i, p2) in enumerate(p1.schedule):
                if p2 is NOBODY:
                    continue
                b = number[p2.name]
                values[(2 + a, 1 + b)] = "round {}".format(i + 1)

        # Create round table too
        start = len(self.people) + 3
        size = 0
        for p1 in self.people:
            if p1.is_present:
                size = max(size, len(p1.schedule))

        if size == 0:
            return values

        for (i, p1) in enumerate(self.people):
            values[(i + 1, start)] = p1.name

        values[(0, start)] = ""
        for i in range(size):
            values[(0, start + i + 1)] = "Round {}".format(i + 1)
            for (j, p1) in enumerate(self.people):
                if i < len(p1.schedule):
                    p2 = p1.schedule[i]
                else:
                    p2 = NOBODY

                if p2 is NOBODY:
                    values[(j + 1, start + i + 1)] = "-"
                else:
                    values[(j + 1, start + i + 1)] = p2.name

        return values

    def to_text(self) -> str:
        out: typing.List[str] = []

        out.append("valid problem? {}\n".format(self.validate_problem()))
        out.append("valid solution? {}\n".format(self.validate_solution()))

        final_round = 0
        present = 0
        for p1 in self.people:
            if p1.is_present:
                present += 1
                for (i, p2) in enumerate(p1.schedule):
                    if (i > final_round) and (p2 is not NOBODY):
                        final_round = i

        num_rounds = final_round + 1
        out.append("number of rounds {}\n".format(num_rounds))
        out.append("number of people present {}\n".format(present))
        out.append("number of people absent {}\n\n".format(len(self.people) - present))

        for p1 in self.people:
            out.append(p1.name)
            out.append("\n")
            out.append("-" * len(p1.name))
            out.append("\n\n")
            if p1.is_present:
                for p2 in p1.already_met:
                    out.append("already met {}\n".format(p2.name))
                for (i, p2) in enumerate(p1.schedule):
                    out.append("meet {} in round {}\n".format(p2.name, i + 1))
            else:
                out.append("not present\n")

            out.append("\n")

        for r in range(num_rounds):
            rname = "Round {}".format(r + 1)
            out.append(rname)
            out.append("\n")
            out.append("-" * len(rname))
            out.append("\n\n")
            for p1 in self.people:
                p2 = NOBODY
                if len(p1.schedule) > r:
                    p2 = p1.schedule[r]

                if (p2 is not NOBODY) and (p1.name < p2.name):
                    out.append("{} meets {}\n".format(p1.name, p2.name))

            out.append("\n")

        return "".join(out)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "people": 
                [
                    {"name": p1.name,
                        "is_present": p1.is_present,
                        "already_met": [p2.name for p2 in p1.already_met],
                        "schedule": [p2.name for p2 in p1.schedule],
                    } for p1 in self.people
                ]
        }

    @staticmethod
    def from_dict(d: typing.Dict[str, typing.Any]) -> "Problem":
        self = Problem()
        lookup: typing.Dict[str, Person] = dict()
        lookup[NOBODY.name] = NOBODY
        for pd in d["people"]:
            p = Person(pd["name"], pd["is_present"])
            self.people.append(p)
            lookup[p.name] = p

        for pd in d["people"]:
            p = lookup[pd["name"]]
            for n in pd["already_met"]:
                p.already_met.append(lookup[n])
            for n in pd["schedule"]:
                p.schedule.append(lookup[n])

        return self

def is_truthy(text: str) -> bool:
    if not text:
        return False

    text = text.lower()
    if text[0] in "-ufn0r":
        return False

    return True


