def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    """
    Cross product of elements in A and elements in B.
    Args:
        A(iterable)
        B(iterable)
    """
    return [s + t for s in A for t in B]

assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

#Adding diagonal_units should make it work for diagonal puzzles
row_units = [cross(r, cols) for r in rows]
col_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ['ABC', 'DEF', 'GHI'] for cs in ['123','456','789']]
diagonal_units = [[rows[i] + cols[i] for i in range(0,9)],[rows[i] + cols[8 - i] for i in range(0,9)]]
unitlist = row_units + col_units + square_units + diagonal_units #Array of units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes) # differents units belonging to s
peers = dict((s, set(sum(units[s], [])) - set(s)) for s in boxes) # all elements in s's units save s

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[rows[i] + cols[i] for i in range(0,9)],[rows[i] + cols[8 - i] for i in range(0,9)]]
unitlist = row_units + col_units + square_units + diagonal_units #Array of units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    def eliminate_value(values, unit, twin):
        # Eliminate the naked twins as possibilities for their peers
        for box in unit:
            if(values[box] != twin):
                assign_value(values, box, values[box].replace(twin[0], ''))
                assign_value(values, box, values[box].replace(twin[1], ''))

    # Find all instances of naked twins
    for unit in unitlist:
        box_options = {} #this will hold counts candidate sequences (twins) found in box
        for box in unit:
            if(len(values[box]) == 2):
                twin = values[box]
                if(twin not in box_options):
                    box_options[twin] = 0
                box_options[twin] += 1
                if(box_options[twin] == 2):
                    #found a naked twin!
                    eliminate_value(values, unit, twin)
        box_options = {}
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    boxes = cross('ABCDEFGHI', '123456789')
    dict = {}
    for i, char in enumerate(grid):
        dict[boxes[i]] = char if char != '.' else '123456789'
    return dict

def display_other(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    output = ''
    width = 1 + max([len(values[k]) for k in values])
    for key in sorted(values):
        output += ' '*((width - len(values[key]))/2) + values[key]  + ' '*((width - len(values[key]))/2)
        output +=  '|' if int(key[1]) % 3 == 0 else ''
        output += '\n' if int(key[1]) % 9 == 0 else ''
    return output

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    knowns = [ind for ind, box in values.items() if len(box) == 1]

    for known in knowns:
        for peer in peers[known]:
            assign_value(values, peer, values[peer].replace(values[known], ''))
            # values[peer] = values[peer].replace(values[known], '')
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        to_check = '123456789'
        for number in to_check:
            #does only one box have this number?
            candidate_boxes = [box for box in unit if values[box].find(number) != -1]
            if len(candidate_boxes) == 1:
                assign_value(values, candidate_boxes[0], number)
                # values[candidate_boxes[0]] = number
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    reduce_puzzle(values)

    # Find naked twins
    naked_twins(values)
    # repeat until stable.

    # Choose one of the unfilled squares with the fewest possibilities
    # Check for squares with more than one possibility (base case for recursion)
    unresolved_keys = [k for k,v in values.items() if len(v) > 1]
    empty_keys = [k for k,v in values.items() if len(v) == 0]
    solution = None

    # Need to choose a value and try it out
    if (len(unresolved_keys) > 0 and len(empty_keys) == 0):
        min_index = unresolved_keys[0] #Want to make sure this has more than one value.
        for index in unresolved_keys:
            min_index = min_index if len(values[min_index]) < len(values[index]) else index

        # Now use recursion to solve each one of the resulting sudokus,
        # and if one returns a value (not False), return that answer!
        candidates = list(values[min_index])
        while len(candidates) > 0 and solution == None:
            candidate_board = values.copy()
            assign_value(candidate_board, min_index, candidates.pop())
            # candidate_board[min_index] = candidates.pop()
            solution = search(candidate_board)
    # Exists box with no possible keys: puzzle not solvable
    elif (len(empty_keys) > 0):
        solution = None
    # reduce_puzzle returned a solved puzzle
    else:
        solution = values

    return solution

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    assignments.append(values.copy())

    #search
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    solution = solve(diag_sudoku_grid)
    display(solution)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
