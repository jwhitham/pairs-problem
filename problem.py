
import typing

MAX_NAMES = 24

class CaptureError(Exception):
    pass

class Person:
    def __init__(self, name: str, is_present: bool) -> None:
        self.name = name
        self.is_present = is_present
        self.already_met: typing.List[Person] = []
        self.schedule: typing.List[Person] = []
    
    def show(self) -> None:
        if not self.is_present:
            return
        print(self.name, "already met:",
                    " ".join([p.name for p in self.already_met]))

NOBODY = Person("*nobody*", False)

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
    def from_spreadsheet(values2: typing.Dict[typing.Tuple[int, int], str],
                    cell_name_fn: typing.Callable[[int, int], str]) -> "Problem":
        # How many names are there?
        num_names = 0
        for i in range(MAX_NAMES):
            if values2.get((0, i + 1), "") or values2.get((i + 2, 0), ""):
                num_names = i + 1

        # Capture names (and check for consistency)
        row_names = set()
        for i in range(num_names):
            name = values2.get((0, i + 1), "")

            if name == "":
                raise CaptureError("Invalid name in cell {}".format(
                            cell_name_fn(0, i + 1)))
            if name.lower() in row_names:
                raise CaptureError("Invalid name in cell {}: duplicate '{}'".format(
                            cell_name_fn(0, i + 1), name))

            if values2.get((i + 2, 0), "") != name:
                raise CaptureError("Invalid name '{}' in cell {} "
                    "- need this name to appear in cell {} too".format(
                            name, cell_name_fn(i + 2, 0), cell_name_fn(0, i + 1)))

            row_names.add(name.lower())

        # Read presence values and create records for people
        self = Problem()
        people = self.people
        for y in range(num_names):
            people.append(Person(name=values2.get((0, y + 1), ""),
                            is_present=is_truthy(values2.get((1, y + 1), ""))))

        # Find out who already talked to whom
        for y in range(num_names):
            for x in range(num_names):
                if (x != y) and is_truthy(values2.get((2 + x, 1 + y), "")):
                    people[x].already_met.append(people[y])
                    people[y].already_met.append(people[x])

        return self

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
    if text[0] in "-fn0":
        return False

    return True


