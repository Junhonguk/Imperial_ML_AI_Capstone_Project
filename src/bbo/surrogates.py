"""GP surrogate factory with per-function options."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel


def transform(y, how):
    """'raw' | 'log' (all-positive, wide range) | 'logabs' (magnitude fields)."""
    if how == "log":
        return np.log(y)
    if how == "logabs":
        return np.log(np.abs(y) + 1e-300)
    return np.asarray(y, dtype=float)


def fit_gp(X, z, noisy=False, ls_hi=10.0, seed=0):
    """Matern 5/2 ARD GP, hyperparameters by MLE.

    noisy=True adds a WhiteKernel (never interpolate noisy data exactly).
    ls_hi caps lengthscales: a cap of ~1-2 forbids the model from declaring
    any dimension 'free' - the fix for sharp-peak functions.
    """
    d = X.shape[1]
    k = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
        length_scale=np.full(d, min(0.3, ls_hi)),
        length_scale_bounds=(1e-2, ls_hi), nu=2.5)
    if noisy:
        k = k + WhiteKernel(1e-2, (1e-8, 1e1))
    gp = GaussianProcessRegressor(kernel=k, normalize_y=True,
                                  n_restarts_optimizer=10, random_state=seed)
    gp.fit(X, z)
    return gp
