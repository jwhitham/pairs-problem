
num_people = 20
state = [chr(x + ord('A')) for x in range(num_people)]

import collections
count = collections.defaultdict(lambda: 0)

with open("test.txt", "wt") as fd:
    fd.write("{}\n".format(num_people))
    for step in range(num_people - 1):
        #print(state)
        for pair in range(num_people // 2):
            a = state[pair]
            b = state[num_people - 1 - pair]
            if a > b:
                (a, b) = (b, a)
            fd.write("{}{} ".format(a, b))
            print("{}{}{} ".format(a, b, count[a + b]), end="")
            count[a + b] += 1
        fd.write("\n")
        state.insert(0, state.pop())
        print("")

from check import check_file
check_file("test.txt")

