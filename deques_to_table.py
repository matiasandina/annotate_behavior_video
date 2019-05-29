# This function aims to prepare deques to save
# It is normally very cumbersome to save deques into tables.
# Instead of doing this over and over again, we can call this function
# We need to do this in pairs because np.append works in pairs

import numpy as np

def deques_to_table(x, y):

    if isinstance(x, np.ndarray):
        # do nothing we like it as is
        print("x is already np.array")
        pass
    else:
        # Convert to np.array
        x = np.array(x)

    if isinstance(y, np.ndarray):
        # do nothing we like it as is
        print("y is already np.array")
        pass
    else:
        # Convert to np.array
        y = np.array(y)

    if min(x.ndim, y.ndim) > 1:
        # throw error
        print("Dimensions are x: " + str(x.ndim) + " and y: " + str(y.ndim))
        raise Exception('At least one argument has to be 1 dimensional.')

    # If both have 1 dimension, we need the [:, None] trick
    if x.ndim == 1 and y.ndim == 1:
        # create the array to save
        array_to_save = np.append(x[:, None],
                                  y[:, None],
                                  axis=1) # Mind axis = 1 to have things in columns
    else:
        # look for that of the max dimension
        if x.ndim > y.ndim:
            array_to_save = np.append(x,
                                     y[:, None],
                                     axis=1)
        else:
            array_to_save = np.append(x[:, None],
                                     y,
                                     axis=1)


    return array_to_save