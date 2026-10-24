"""Fitting of data dependencies for model."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pymetadata.console import console
from scipy.optimize import curve_fit

# TODO: set random seed for the optimization


def saturation_func(x: np.ndarray, v: float, k: float) -> np.ndarray:
    """Saturation with maximum v and IC50 k for half-saturation.

    dose_dependent_change = f(dose) = v * dose / (k + dose)
    """
    return v * x / (k + x)


def linear_func(x: np.ndarray, m: float) -> np.ndarray:
    """Linear fit through the origin: y = m * x."""
    return m * x


def linear_func_intercept(x: np.ndarray, m: float, c: float) -> np.ndarray:
    """Linear fit with intercept: y = m * x + c."""
    return m * x + c


def fit_dose_dependency(df: pd.DataFrame, pd_name: str) -> np.ndarray:
    """Fit saturation_func to `{pd_name}_delta` ~ dose_mg, returning optimal (v, k)."""
    # filter to only applications of dulaglutide or placebo
    mask_dose = df["intervention"].str.startswith(("DUL", "PLAC"))
    df_filtered = df[mask_dose]

    xdata_raw = df_filtered["dose_mg"].values
    ydata_raw = df_filtered[f"{pd_name}_delta"].values
    n_raw = df_filtered["n"].values

    # remove nans/infs from both axes before fitting
    mask_na = np.isfinite(ydata_raw) & np.isfinite(xdata_raw)
    xdata = xdata_raw[mask_na]
    ydata = ydata_raw[mask_na]
    n = n_raw[mask_na]

    # FIXME: weighted curve fitting
    popt, _pcov = curve_fit(saturation_func, xdata, ydata)
    console.print(f"{popt=}")
    # v = popt[0]; k = popt[1]
    console.print(f"f(dose) = {popt[0]} * dose / ({popt[1]} + dose)")

    # placebo effect (dose = 0 mg)
    placebo_index = np.where(np.isclose(xdata, 0.0))
    placebo_effect_vec = ydata[placebo_index]
    n_vec = n[placebo_index]
    console.print(f"{placebo_effect_vec=}")
    console.print(f"{n_vec=}")
    placebo_effect = np.average(placebo_effect_vec, weights=n_vec)
    console.print(f"{placebo_effect=}")

    # placebo effect dose
    # y = v * x / (k + x)
    # y*k + y*x = v*x
    # x = y*k/(v-y)
    placebo_dose = placebo_effect * popt[1] / (popt[0] - placebo_effect)
    console.print(f"{placebo_dose=}")

    return popt


def fit_linear_regression(df: pd.DataFrame, x_name: str, y_name: str) -> np.ndarray:
    """Fit linear_func to `y_name` ~ `x_name`, returning optimal (m,)."""
    # filter to only applications of dulaglutide or placebo
    mask_dose = df["intervention"].str.startswith(("DUL", "PLAC"))
    df_filtered = df[mask_dose]

    xdata_raw = df_filtered[x_name].values
    ydata_raw = df_filtered[y_name].values

    # remove nans/infs from both axes before fitting
    mask_na = np.isfinite(ydata_raw) & np.isfinite(xdata_raw)
    xdata = xdata_raw[mask_na]
    ydata = ydata_raw[mask_na]

    popt, _pcov = curve_fit(linear_func, xdata, ydata)
    return popt


def fit_pd_dose_dependency_function(df: pd.DataFrame, pd_name: str) -> None:
    """Fit function to the PD data and plot the result."""
    # filter to only applications of dulaglutide or placebo
    mask_dose = df["intervention"].str.startswith(("DUL", "PLAC"))
    df_filtered = df[mask_dose]

    xdata_raw = df_filtered["dose_mg"].values
    ydata_raw = df_filtered[f"{pd_name}_delta"].values
    sigma_raw = df_filtered[f"{pd_name}_delta_sd"].values

    # remove nans/infs from both axes before fitting
    mask_na = np.isfinite(ydata_raw) & np.isfinite(xdata_raw)
    xdata = xdata_raw[mask_na]
    ydata = ydata_raw[mask_na]
    sigma = sigma_raw[mask_na]

    # sort data by xvalues
    sort_idx = np.argsort(xdata)
    xdata = xdata[sort_idx]
    ydata = ydata[sort_idx]
    sigma = sigma[sort_idx]

    popt = fit_dose_dependency(df, pd_name)

    _fig, ax = plt.subplots(figsize=(11, 9))
    ax.errorbar(
        x=xdata,
        y=ydata,
        yerr=sigma,
        marker="s",
        markeredgecolor="k",
        linestyle="",
        color="darkgray",
        label="data",
    )
    # ax.plot(xdata, y0, color="tab:blue", lw=1, label="guess")

    y_est = saturation_func(xdata, *popt)
    ax.plot(xdata, y_est, color="tab:green", linestyle="", marker="o", label="fit")

    xeval = np.linspace(start=xdata.min(), stop=xdata.max(), num=100)
    yeval = saturation_func(xeval, *popt)
    ax.plot(xeval, yeval, color="tab:green", linestyle="-", marker="", label="fit")

    ax.set_title(f"{pd_name}_delta ~ dose (n={len(xdata)})")
    ax.legend()
    # limits = [5, 15]
    # ax.set_xlim([-0.5, 2.5])
    # ax.set_ylim([-4, 0])
    ax.set_xlabel("dose [mg]")
    ax.set_ylabel(f"{pd_name}_delta [mM]")  # maximum change

    plt.show()


def _impute_missing_sd(
    sd: np.ndarray, mean: np.ndarray, n: np.ndarray, label: str
) -> np.ndarray:
    """Impute missing SDs from the n-weighted mean coefficient of variation.

    The coefficient of variation (CV = sd/|mean|) is observed for this outcome, scaled by each row's own mean (Cochrane-style borrowing of
    *relative* variance across arms).
    """
    missing = ~np.isfinite(sd)
    if missing.any():
        observed = ~missing
        cv_observed = observed & (mean != 0)
        cv = sd[cv_observed] / np.abs(mean[cv_observed])
        cv_impute = np.average(cv, weights=n[cv_observed])

        sd = sd.copy()
        missing_nonzero = missing & (mean != 0)
        sd[missing_nonzero] = cv_impute * np.abs(mean[missing_nonzero])
        console.print(
            f"[{label}] imputing sd for {missing_nonzero.sum()} row(s) missing sd "
            f"with n-weighted mean CV={cv_impute:.4g} (sd = CV * |mean|)"
        )

        # CV is undefined for a zero mean (would impute sd=0, i.e. infinite weight);
        # fall back to the n-weighted mean absolute sd observed for this outcome.
        missing_zero = missing & (mean == 0)
        if missing_zero.any():
            sd_impute = np.average(sd[observed], weights=n[observed])
            sd[missing_zero] = sd_impute
            console.print(
                f"[{label}] imputing sd for {missing_zero.sum()} row(s) with mean=0 "
                f"(CV undefined) using n-weighted mean sd={sd_impute:.4g}"
            )
    return sd


def _saturation_jac(x: np.ndarray, v: float, k: float) -> np.ndarray:
    """Jacobian of saturation_func w.r.t. (v, k), evaluated at (v, k)."""
    return np.column_stack([x / (k + x), -v * x / (k + x) ** 2])


def _linear_jac(x: np.ndarray, m: float) -> np.ndarray:
    """Jacobian of linear_func w.r.t. (m,), evaluated at (m,)."""
    return x.reshape(-1, 1)


def _linear_intercept_jac(x: np.ndarray, m: float, c: float) -> np.ndarray:
    """Jacobian of linear_func_intercept w.r.t. (m, c), evaluated at (m, c)."""
    return np.column_stack([x, np.ones_like(x)])


def _weighted_curve_fit(
    func: Callable[..., np.ndarray],
    jac_func: Callable[..., np.ndarray],
    xdata: np.ndarray,
    ydata: np.ndarray,
    sd: np.ndarray,
    n: np.ndarray,
    random_effects: bool,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Weighted nonlinear least squares with an optional DerSimonian-Laird tau^2 term.

    jac_func(xdata, *popt) gives the Jacobian of `func` w.r.t. its parameters,
    evaluated at the fixed-effect optimum; it stands in for the linear design matrix X
    in the generalized DL denominator C = tr(W) - tr[(J'WJ)^-1 (J'W^2J)], which has no
    closed form for a nonlinear model.
    """
    vi = sd**2 / n

    # fixed-effect fit (plain inverse-variance weights) to get residuals/Jacobian
    popt, _pcov = curve_fit(func, xdata, ydata, sigma=np.sqrt(vi), absolute_sigma=True)

    if random_effects:
        wi = 1 / vi
        resid = ydata - func(xdata, *popt)
        Q = np.sum(wi * resid**2)
        n_obs, p = len(xdata), len(popt)

        J = jac_func(xdata, *popt)
        JtWJ = J.T @ (J * wi[:, None])
        JtW2J = J.T @ (J * (wi**2)[:, None])
        C = np.sum(wi) - np.trace(np.linalg.solve(JtWJ, JtW2J))

        tau2 = max(0.0, (Q - (n_obs - p)) / C) if C > 0 else 0.0
        sigma_final = np.sqrt(vi + tau2)
    else:
        tau2 = 0.0
        sigma_final = np.sqrt(vi)

    popt, pcov = curve_fit(
        func, xdata, ydata, sigma=sigma_final, absolute_sigma=True, p0=popt
    )
    return popt, pcov, tau2


@dataclass
class WeightedFitResult:
    """Result of a weighted saturation_func (v*x/(k+x)) dose-response fit."""

    params: np.ndarray  # [v, k]
    bse: np.ndarray  # standard errors of [v, k]
    pcov: np.ndarray
    tau2: float

    def summary(self) -> str:
        """Return the fitted function with its parameters and standard errors."""
        v, k = self.params
        v_se, k_se = self.bse
        return (
            f"f(dose) = {v:.4g} * dose / ({k:.4g} + dose)\n"
            f"v = {v:.4g} +/- {v_se:.4g}\n"
            f"k = {k:.4g} +/- {k_se:.4g}\n"
            f"tau^2 = {self.tau2:.4g}"
        )


@dataclass
class WeightedLinearFitResult:
    """Result of a weighted linear regression: y = m*x (zero-intercept) or y = m*x + c."""

    params: np.ndarray  # [m] or [m, c]
    bse: np.ndarray  # standard error(s) matching params
    pcov: np.ndarray
    tau2: float

    def summary(self) -> str:
        """Return the fitted line with its parameters and standard errors."""
        m = self.params[0]
        m_se = self.bse[0]
        if self.params.size > 1:
            c = self.params[1]
            c_se = self.bse[1]
            return (
                f"y = {m:.4g} * x + {c:.4g}\n"
                f"m = {m:.4g} +/- {m_se:.4g}\n"
                f"c = {c:.4g} +/- {c_se:.4g}\n"
                f"tau^2 = {self.tau2:.4g}"
            )
        return f"y = {m:.4g} * x\nm = {m:.4g} +/- {m_se:.4g}\ntau^2 = {self.tau2:.4g}"


def fit_weighted_pd_dose_dependency_function(
    df: pd.DataFrame,
    pd_name: str,
    n_col: str = "n",
    random_effects: bool = True,
    impute_missing_sd: bool = True,
    plot: bool = True,
    ax: plt.Axes | None = None,
) -> WeightedFitResult:
    """Fit a weighted saturation_func dose-response curve for one PD outcome and plot it.

    Parameters
    ----------
    df : dataframe with columns "dose_mg", f"{pd_name}_delta", f"{pd_name}_delta_sd",
         and a sample-size column.
    pd_name : outcome name, e.g. "glucose"
    n_col : name of the per-row sample-size column. Defaults to "n".
    random_effects : if True, add DerSimonian-Laird tau^2 to the weights (recommended
        when n varies a lot across studies). If False, use plain inverse-variance weights.
    impute_missing_sd : boolean value that determines whether missing sd values should be imputed to prevent omission of study data
    plot : if True, draw the errorbar/fit plot (into `ax`, or a new figure if `ax`
        is None). If False, only fit and return the result.
    ax : optional existing axes to plot into (ignored if `plot` is False).

    Returns:
    -------
    A WeightedFitResult with the fitted [v, k] in .params and their standard errors in .bse.
    """
    mask_dose = df["intervention"].str.startswith(("DUL", "PLAC"))
    df_filtered = df[mask_dose]

    xdata_raw = df_filtered["dose_mg"].values
    ydata_raw = df_filtered[f"{pd_name}_delta"].values
    sd_raw = df_filtered[f"{pd_name}_delta_sd"].values.astype(float)
    n_raw = df_filtered[n_col].values

    required_finite = (
        np.isfinite(xdata_raw) & np.isfinite(ydata_raw) & np.isfinite(n_raw)
    )
    if impute_missing_sd:
        mask_na = required_finite
    else:
        mask_na = required_finite & np.isfinite(sd_raw)

    xdata, ydata, sd, n = (
        xdata_raw[mask_na],
        ydata_raw[mask_na],
        sd_raw[mask_na],
        n_raw[mask_na],
    )

    if impute_missing_sd:
        sd = _impute_missing_sd(sd, ydata, n, label=pd_name)

    sort_idx = np.argsort(xdata)
    xdata, ydata, sd, n = xdata[sort_idx], ydata[sort_idx], sd[sort_idx], n[sort_idx]

    popt, pcov, tau2 = _weighted_curve_fit(
        saturation_func, _saturation_jac, xdata, ydata, sd, n, random_effects
    )
    bse = np.sqrt(np.diag(pcov))

    if plot:
        if ax is None:
            _fig, ax = plt.subplots(figsize=(11, 9))

        ax.errorbar(
            x=xdata,
            y=ydata,
            yerr=sd,
            marker="s",
            markeredgecolor="k",
            linestyle="",
            color="darkgray",
            label="data",
        )

        xeval = np.linspace(xdata.min(), xdata.max(), 100)
        yeval = saturation_func(xeval, *popt)
        ax.plot(xeval, yeval, color="tab:green", linestyle="-", label="weighted fit")

        tau_str = f", tau²={tau2:.3g}" if random_effects else ""
        ax.set_title(f"{pd_name}_delta ~ dose (n_studies={len(xdata)}{tau_str})")
        ax.legend()
        ax.set_xlabel("dose [mg]")
        ax.set_ylabel(f"{pd_name}_delta [mM]")

    return WeightedFitResult(params=popt, bse=bse, pcov=pcov, tau2=tau2)


def fit_weighted_linear_regression(
    df: pd.DataFrame,
    x_name: str,
    y_name: str,
    n_col: str = "n",
    random_effects: bool = True,
    impute_missing_sd: bool = True,
    fit_intercept: bool = False,
    plot: bool = True,
    ax: plt.Axes | None = None,
) -> WeightedLinearFitResult:
    """Fit a weighted linear regression of `y_name` ~ `x_name` and plot it.

    Weights come from the sampling variance of the y-axis outcome only
    (f"{y_name}_sd"**2 / n); x is treated as fixed, mirroring
    fit_weighted_pd_dose_dependency_function.

    Parameters
    ----------
    df : dataframe with columns x_name, y_name, f"{y_name}_sd", and a sample-size column.
    x_name, y_name : e.g. "fpg_delta", "hba1c_delta"
    n_col : name of the per-row sample-size column. Defaults to "n".
    random_effects : if True, add DerSimonian-Laird tau^2 to the weights.
    impute_missing_sd :  boolean value that determines whether missing sd values should be imputed to prevent omission of study data
    fit_intercept : if True, fit y = m*x + c (with intercept c). If False (default),
        fit the zero-intercept model y = m*x.
    plot : if True, draw the errorbar/fit plot (into `ax`, or a new figure if `ax`
        is None). If False, only fit and return the result.
    ax : optional existing axes to plot into (ignored if `plot` is False).

    Returns:
    -------
    A WeightedLinearFitResult with the fitted parameters ([m] or [m, c]) in .params
    and their standard errors in .bse.
    """
    mask_dose = df["intervention"].str.startswith(("DUL", "PLAC"))
    df_filtered = df[mask_dose]

    xdata_raw = df_filtered[x_name].values
    ydata_raw = df_filtered[y_name].values
    sd_raw = df_filtered[f"{y_name}_sd"].values.astype(float)
    n_raw = df_filtered[n_col].values

    required_finite = (
        np.isfinite(xdata_raw) & np.isfinite(ydata_raw) & np.isfinite(n_raw)
    )
    if impute_missing_sd:
        mask_na = required_finite
    else:
        mask_na = required_finite & np.isfinite(sd_raw)

    xdata, ydata, sd, n = (
        xdata_raw[mask_na],
        ydata_raw[mask_na],
        sd_raw[mask_na],
        n_raw[mask_na],
    )

    if impute_missing_sd:
        sd = _impute_missing_sd(sd, ydata, n, label=y_name)

    sort_idx = np.argsort(xdata)
    xdata, ydata, sd, n = xdata[sort_idx], ydata[sort_idx], sd[sort_idx], n[sort_idx]

    func = linear_func_intercept if fit_intercept else linear_func
    jac_func = _linear_intercept_jac if fit_intercept else _linear_jac

    popt, pcov, tau2 = _weighted_curve_fit(
        func, jac_func, xdata, ydata, sd, n, random_effects
    )
    bse = np.sqrt(np.diag(pcov))

    if plot:
        if ax is None:
            _fig, ax = plt.subplots(figsize=(11, 9))

        ax.errorbar(
            x=xdata,
            y=ydata,
            yerr=sd,
            marker="s",
            markeredgecolor="k",
            linestyle="",
            color="darkgray",
            label="data",
        )

        xmin, xmax = min(0, xdata.min()), max(0, xdata.max())
        xeval = np.linspace(xmin, xmax, 100)
        yeval = func(xeval, *popt)
        ax.plot(xeval, yeval, color="tab:green", linestyle="-", label="weighted fit")

        tau_str = f", tau²={tau2:.3g}" if random_effects else ""
        ax.set_title(f"{y_name} ~ {x_name} (n_studies={len(xdata)}{tau_str})")
        ax.legend()
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)

    return WeightedLinearFitResult(params=popt, bse=bse, pcov=pcov, tau2=tau2)


if __name__ == "__main__":
    data_path = Path(__file__).resolve().parent / "baseline.csv"
    df = pd.read_csv(data_path)
    console.print(df.columns)
    pd_list = [
        "fpg",
        "hba1c",
        "bw",
    ]
    for pd_name in pd_list:
        console.rule(pd_name, style="white", align="left")
        fit_pd_dose_dependency_function(df=df, pd_name=pd_name)

        fit = fit_weighted_pd_dose_dependency_function(df=df, pd_name=pd_name)
        console.print(fit.summary())
        plt.show()

    # fpg_change ~ dose = -3.49283418 * dose/(0.58913256 + dose)
