# This function is used to crop the last part of a deque
# It is used to get the "unsaved elements" on a deque that is saved every n iterations

# This saving is a bit difficult to understand...use a toy example with 7 frames and 5 of buffer
# Reminder is 2, you want elements 7 and 8 from deque
# To say that to python you need the len(x) - unsaved_elements + 1, up to the length of the deque

import itertools

def crop_deque(x, unsaved_elements):

    x = list(itertools.islice(x,
                              len(x) - unsaved_elements + 1,  # from
                              len(x)))  # to
    return (x)