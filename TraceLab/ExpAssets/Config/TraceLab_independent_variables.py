from klibs.KLIndependentVariable import IndependentVariableSet


# Initialize object containing project's factor set

TraceLab_ind_vars = IndependentVariableSet()


# Define project variables and variable types

TraceLab_ind_vars.add_variable("animate_time", int, [1500])
TraceLab_ind_vars.add_variable("figure_name", str, ["random", "template_1477090164.31"])
TraceLab_ind_vars.add_variable("stim_trial", bool, [True, False])
