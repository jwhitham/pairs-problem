
import random
import collections

class Counsellor:
    def __init__(self, name: str) -> None:
        self.name = name
        self.seen = set()
        self.seen.add(self)
        self.allocated = None
        self.priority1 = 0
        self.priority2 = 0

COUNSELLORS = [Counsellor(chr(x + ord('A'))) for x in range(18)]

def test(assign_priority):
    dist = collections.defaultdict(lambda: 0)
    for run in range(10000):
        free1 = COUNSELLORS[:]
        for a in free1:
            a.allocated = None
            a.seen = set()
            a.seen.add(a)

        iteration = 0
        progress = True
        while progress:
            iteration += 1
            free1 = COUNSELLORS[:]
            free2 = COUNSELLORS[:]
            for a in free1:
                a.allocated = None
                a.priority1 = a.name
                a.priority2 = a.name
                assign_priority(a)

            free1.sort(key = lambda a: a.priority1)
            free2.sort(key = lambda a: a.priority2)
            progress = False
            while len(free1) > 1:
                a = free1.pop(0)
                free2.remove(a)
                assert a.allocated is None
                valid = False
                for i in range(len(free2)):
                    b = free2[i]
                    if not (b in a.seen):
                        valid = True
                        break

                if valid:
                    assert a != b
                    assert a.allocated is None
                    assert b.allocated is None
                    assert not (b in a.seen)
                    assert not (a in b.seen)
                    free1.remove(b)
                    free2.remove(b)
                    a.allocated = b
                    b.allocated = a
                    a.seen.add(b)
                    b.seen.add(a)
                    #print(a.name, "+", b.name)
                    progress = True
            #print("")

        for a in COUNSELLORS:
            assert a.seen == set(COUNSELLORS)
        
        dist[iteration] += 1
    
    print(dist.items())

def d20(a):
    a.priority1 = (len(a.seen), random.randint(1, 20))
    a.priority2 = a.priority1

test(d20)
