from pyformlang.regular_expression import Regex
import os

EPS_SYM = 'eps'
SUPPORTED_REGEX_CHARS = '.*()?|'


def RPQ_to_nfa(lines, out):
    for l in lines[2:]:
        pr = l.split(' -> ')
        body_str = pr[1].rstrip('\n')

        # pyformlang doesn't accept '?' quantifier, transforming to alternative expression
        body_str = body_str.replace('?', f'|{EPS_SYM}')

        enfa = Regex(body_str).to_epsilon_nfa()
        enfa = enfa.minimize()

        transitions = enfa._transition_function._transitions

        # create map for state names (original names are so big)
        map_states = dict()
        count_states = 0
        for state in enfa.states:
            map_states.update({state: count_states})
            count_states += 1

        # create list of transitions (edge)
        list_edges = list()
        for state in enfa.states:
            if transitions.get(state) is not None:
                for key in transitions.get(state):
                    list_edges.append([map_states[state], key, map_states[transitions.get(state)[key]]])

        # create true file format for nfa
        set_label = set()
        true_format = list()
        size_matrix = 0
        for edge in list_edges:
            if edge[1] not in set_label:
                current_edge = [edge[1]]
                for edge_1 in list_edges:
                    if edge[1] == edge_1[1]:
                        if size_matrix < edge_1[0]:
                            size_matrix = edge_1[0]
                        if size_matrix < edge_1[2]:
                            size_matrix = edge_1[2]
                        current_edge.append([edge_1[0], edge_1[2]])
                true_format.append(current_edge)
                set_label.add(edge[1])

        map_digit_to_word = {i: ord(i + 65) for i in range(11)}

        # write to output
        with open(out, "w") as file:
            file.write(str(len(set_label)) + "\n")
            file.write("1" + "\n")
            file.write(str(size_matrix + 1) + "\n")
            for i in true_format:
                file.write(str(map_digit_to_word[i[0]]) + "\n")
                current_size = len(i)
                for j in range(1, current_size):
                    file.write(str(i[j][0]) + " " + str(i[j][1]) + "\n")

            file.write("S" + "\n")
            for state in enfa.final_states:
                file.write("0" + " " + str(map_states[state]) + "\n")


def main():
    files = [str(i) for i in range(10)]
    print(files)
    directories = os.listdir("../../../RPQ/taxonomy_data/taxonomy_queries")
    print(directories)
    for directory in directories:
        if directory == "q_12" or directory == "q_13":
            continue
        input = "../../../RPQ/taxonomy_data/taxonomy_queries/" + directory + "/"
        output = "../../../RPQ/taxonomy_data/taxonomy_automat/" + directory
        os.mkdir(output)
        output += "/"
        for file in files:
            input += file
            output += file
            RPQ_to_nfa(open(input, "r").readlines(), output)
            input = input[:-1]
            output = output[:-1]


if __name__ == "__main__":
    main()