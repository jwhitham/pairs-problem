

import collections, configparser
count = collections.defaultdict(lambda: 0)
meetings = collections.defaultdict(lambda: [])

parser = configparser.ConfigParser(allow_no_value=True)
parser.read("input.txt")
names = sorted(parser.sections())
num_people = len(names)
state = names[:]
if (num_people % 2) == 1:
    state.append("")


with open("test.txt", "wt") as fd:
    stop = False
    for step in range(num_people - 1):
        #print(state)
        for pair in range(num_people // 2):
            a = state[pair]
            b = state[num_people - 1 - pair]
            if a > b:
                (a, b) = (b, a)

            if count[a + b] != 0:
                stop = True
                break
           
            if a != "" and b != "":
                meetings[a].append(b)
                meetings[b].append(a)
                count[a + b] += 1

        if stop:
            break

        state.insert(0, state.pop())

    for a in names:
        fd.write("[{}]\n".format(a))
        for b in meetings[a]:
            fd.write("{}\n".format(b))

        fd.write("\n")

#from check import check_file
#check_file("test.txt")

