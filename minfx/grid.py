###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2008-2009 Edward d'Auvergne                       #
#                                                                             #
# This file is part of the minfx optimisation library.                        #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from numpy import float64, ones, zeros

# Minfx module imports.
from constraint_linear import Constraint_linear
from errors import MinfxError


def grid(func, args=(), num_incs=None, lower=None, upper=None, incs=None, A=None, b=None, l=None, u=None, c=None, verbosity=0, print_prefix=""):
    """The grid search algorithm.

    @param func:            The target function.  This should take the parameter vector as the first
                            argument and return a single float.
    @type func:             function
    @keyword args:          A tuple of arguments to pass to the function, if needed.
    @type args:             tuple
    @keyword num_incs:      The number of linear increments to be used in the grid search.  The
                            length should be equal to the number of parameters and each element
                            corresponds to the number of increments for the respective parameter.
                            This is overridden if the incs argument is supplied.
    @type num_incs:         list of int
    @keyword lower:         The list of lower bounds for the linear grid search.  This must be
                            supplied if incs is not.
    @type lower:            list of float
    @keyword upper:         The list of upper bounds for the linear grid search.  This must be
                            supplied if incs is not.
    @type upper:            list of float
    @keyword incs:          The parameter increment values.  This overrides the num_incs, lower, and
                            upper arguments used in generating a linear grid.
    @type incs:             list of lists
    @keyword A:             The linear constraint matrix A, such that A.x >= b.
    @type A:                numpy rank-2 array
    @keyword b:             The linear constraint scalar vectors, such that A.x >= b.
    @type b:                numpy rank-1 array
    @keyword l:             The lower bound constraint vector, such that l <= x <= u.
    @type l:                list of float
    @keyword u:             The upper bound constraint vector, such that l <= x <= u.
    @type u:                list of float
    @keyword c:             A user supplied constraint function.
    @type c:                function
    @keyword verbosity:     The verbosity level.  0 corresponds to no output, 1 is standard, and
                            higher values cause greater and greater amount of output.
    @type verbosity:        int
    @keyword print_prefix:  The text to place before the printed output.
    @type print_prefix:     str
    @return:                The optimisation information including the parameter vector at the best
                            grid point, the function value at this grid point, the number of
                            iterations (equal to the number of function calls), and a warning.
    @rtype:                 tuple of numpy rank-1 array, float, int, str
    """

    # Checks.
    if num_incs == None and incs == None:
        raise MinfxError("Either the incs arg or the num_incs, lower, and upper args must be supplied.")
    elif num_incs:
        # Check that this is a list.
        if not isinstance(num_incs, list):
            raise MinfxError("The num_incs argument '%s' must be a list." % num_incs)
        if not isinstance(lower, list):
            raise MinfxError("The lower argument '%s' must be a list." % lower)
        if not isinstance(upper, list):
            raise MinfxError("The upper argument '%s' must be a list." % upper)

        # Lengths.
        if len(num_incs) != len(lower):
            raise MinfxError("The '%s' num_incs and '%s' lower arguments are of different lengths" % (num_incs, lower))
        if len(num_incs) != len(upper):
            raise MinfxError("The '%s' num_incs and '%s' upper arguments are of different lengths" % (num_incs, upper))

    # Catch models with zero parameters.
    if num_incs == [] or incs == []:
        # Print out.
        if verbosity:
            print("Cannot run a grid search on a model with zero parameters, directly calculating the function value.")

        # Empty parameter vector.
        x0 = zeros(0, float64)

        # The function value.
        fk = func(x0)

        # The results tuple.
        return x0, fk, 1, "No optimisation"


    # Initialise.
    if num_incs:
        n = len(num_incs)
    else:
        n = len(incs)
    grid_size = 0
    total_steps = 1
    step_num = ones(n, int)
    params = zeros((n), float64)
    min_params = zeros((n), float64)

    # Linear grid search.
    # The incs data structure eliminates the round-off error of summing a step size value to the parameter value.
    if num_incs:
        incs = []
        for k in xrange(n):
            params[k] = lower[k]
            min_params[k] = lower[k]
            total_steps = total_steps * num_incs[k]
            incs.append([])
            for i in xrange(num_incs[k]):
                incs[k].append(lower[k] + i * (upper[k] - lower[k]) / (num_incs[k] - 1))

    # User supplied grid search.
    else:
        for k in xrange(n):
            total_steps = total_steps * len(incs[k])

    # Print out.
    if verbosity:
        if verbosity >= 2:
            print print_prefix
        print print_prefix
        print print_prefix + "Grid search"
        print print_prefix + "~~~~~~~~~~~"

    # Linear constraints.
    if A != None and b != None:
        constraint_flag = 1
        constraint_linear = Constraint_linear(A, b)
        c = constraint_linear.func
        if verbosity >= 3:
            print print_prefix + "Linear constraint matrices."
            print print_prefix + "A: " + `A`
            print print_prefix + "b: " + `b`

    # Bound constraints.
    elif l != None and u != None:
        constraint_flag = 1
        raise MinfxError("Bound constraints are not implemented yet.")

    # General constraints.
    elif c != None:
        constraint_flag = 1

    # No constraints.
    else:
        constraint_flag = 0

    # Set a ridiculously large initial grid value.
    f_min = 1e300

    # Initial print out.
    if verbosity:
        print "\n" + print_prefix + "Searching through %s grid nodes." % total_steps

    # Test if the grid is too large.
    if total_steps >= 1e8:
        raise MinfxError("A grid search of size %s is too large." % total_steps)

    # Search the grid.
    k = 0
    for i in xrange(total_steps):
        # Check that the grid point does not violate a constraint, and if it does, skip the function call.
        skip = 0
        if constraint_flag:
            ci = c(params)
            if min(ci) < 0.0:
                if verbosity >= 3:
                    print print_prefix + ("k: %-8i xk: [ " + "%11.5g, "*(n-1) + "%11.5g]") % ((k,) + tuple(min_params))
                    print print_prefix + "Constraint violated, skipping grid point."
                    print print_prefix + "ci: " + `ci`
                    print ""
                skip = 1

        # Function call, test, and increment grid_size.
        if not skip:
            # Back calculate the current function value.
            f = func(*(params,)+args)

            # Test if the current function value is less than the least function value.
            if f < f_min:
                f_min = f
                min_params = 1.0 * params

                # Print out code.
                if verbosity:
                    print print_prefix + ("k: %-8i xk: [ " + "%11.5g, "*(n-1) + "%11.5g] fk: %-20s") % ((k,) + tuple(min_params) + (f_min,))

            # Grid count.
            grid_size = grid_size + 1

            # Print out code.
            if verbosity >= 2:
                if f != f_min:
                    print print_prefix + ("k: %-8i xk: [ " + "%11.5g, "*(n-1) + "%11.5g] fk: %-20s") % ((k,) + tuple(min_params) + (f,))
                if verbosity >= 3:
                    print print_prefix + "%-20s%-20s" % ("Increment:", `step_num`)
                    print print_prefix + "%-20s%-20s" % ("Params:", `params`)
                    print print_prefix + "%-20s%-20s" % ("Min params:", `min_params`)
                    print print_prefix + "%-20s%-20g\n" % ("f:", f)
                    print print_prefix + "%-20s%-20g\n" % ("Min f:", f_min)

            # Increment k.
            k = k + 1

        # Increment the grid search.
        for j in xrange(n):
            if step_num[j] < len(incs[j]):
                step_num[j] = step_num[j] + 1
                params[j] = incs[j][step_num[j]-1]
                break    # Exit so that the other step numbers are not incremented.
            else:
                step_num[j] = 1
                params[j] = incs[j][0]

    # Return the results.
    return min_params, f_min, grid_size, None
