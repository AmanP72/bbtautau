'''''

import json
import pyhf

# use Minuit2 as minimizer through iminuit
pyhf.set_backend("numpy", pyhf.optimize.minuit_optimizer(verbose=True))

with open("/Users/amanpritam/Documents/Root_Project_1/mA50.json", "r") as f:
    spec = json.load(f)

workspace = pyhf.Workspace(spec)
model = workspace.model()
data = workspace.data(model)

# run the fit
result = pyhf.infer.mle.fit(data, model, return_uncertainties=True)

# format parameter names
def get_parameter_names(model):
    labels = []
    for parname in model.config.par_order:
        for i_par in range(model.config.param_set(parname).n_parameters):
            labels.append(
                "{}[bin_{}]".format(parname, i_par)
                if model.config.param_set(parname).n_parameters > 1
                else parname
            )
    return labels

bestfit = result[:, 0]
uncertainty = result[:, 1]
labels = get_parameter_names(model)

# show results
for i, label in enumerate(labels):
    print(f"{label}: {bestfit[i]} +/- {uncertainty[i]}")

'''''



import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pyhf

with open("/Users/amanpritam/Documents/Root_Project_1/mA50.json", "r") as f:
    spec = json.load(f)

workspace = pyhf.Workspace(spec)
model = workspace.model()  
data = workspace.data(model)


pyhf.set_backend("numpy", "minuit")


pyhf.optimizer.tolerance
pyhf.set_backend(pyhf.tensorlib, pyhf.optimize.minuit_optimizer(tolerance=1e-3))


result = pyhf.infer.mle.fit(data, model, return_uncertainties=True)
result[:5]