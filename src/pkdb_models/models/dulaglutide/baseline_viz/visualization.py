"""Scatter plots of the baseline values and their change under dulaglutide."""

from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pymetadata.console import console

from pkdb_models.models.dulaglutide.baseline_viz.fit_curves import (
    fit_weighted_linear_regression,
    linear_func,
    linear_func_intercept,
    saturation_func,
)

AXIS_LABELS = {
    "fpg_init": "Initial FPG",
    "fpg_low": "Lowest FPG",
    "fpg_delta": "Change in FPG",
    "hba1c_init": "Initial HbA1c",
    "hba1c_low": "Lowest HbA1c",
    "hba1c_delta": "Change in HbA1c",
    "bw_init": "Initial bodyweight",
    "bw_low": "Lowest bodyweight",
    "bw_delta": "Change in bodyweight",
    "dose_mg": "Dose",
}

UNITS = {
    "fpg": "mM",
    "hba1c": "%",
    "bw": "kg",
    "dose_mg": "mg",
}


def _label_with_unit(var: str) -> str:
    label = AXIS_LABELS.get(var, var)
    unit = UNITS.get(var) or UNITS.get(var.split("_")[0])
    return f"{label} ({unit})" if unit else label


MARKERS = {"T2DM": "o", "Healthy": "s"}

AXIS_LIMITS = {
    "fpg_delta": (-5, 1),
    "hba1c_delta": (-2.5, 0.5),
    "bw_delta": (-5, 2),
}

# marker area (points^2) mapped to sample size n
MARKER_SIZE_RANGE = (20, 300)


def n_to_size(n: float, n_min: float, n_max: float) -> float:
    """Sqrt-scale sample size n to marker area so visual area ~ n."""
    frac = (np.sqrt(n) - np.sqrt(n_min)) / (np.sqrt(n_max) - np.sqrt(n_min))
    return MARKER_SIZE_RANGE[0] + frac * (MARKER_SIZE_RANGE[1] - MARKER_SIZE_RANGE[0])


def _prepare_pair_df(
    df: pd.DataFrame, x: str, y: str, error_key: str = "sd"
) -> pd.DataFrame:
    if x == "dose_mg" or y == "dose_mg":
        df = df[
            [
                "study",
                "sid",
                "intervention",
                "health",
                "n",
                x,
                f"{x}_{error_key}",
                y,
                f"{y}_{error_key}",
            ]
        ]
    else:
        df = df[
            [
                "study",
                "sid",
                "intervention",
                "health",
                "n",
                "dose_mg",
                x,
                f"{x}_{error_key}",
                y,
                f"{y}_{error_key}",
            ]
        ]
    return df.dropna(subset=[x, y]).reset_index(drop=True)


def scatter_on_ax(
    ax: plt.Axes,
    df: pd.DataFrame,
    x: str,
    y: str,
    norm: mcolors.Normalize,
    cmap: mcolors.Colormap,
    n_min: float,
    n_max: float,
    error_key: str,
    annotate_points: bool = True,
) -> None:
    """Draw the scatter of y against x on ax, colored by dose and sized by n."""
    # zero lines only make sense as a reference when zero is a meaningful value
    # for that axis (dose=0 is placebo, delta=0 is no change); baseline values
    # (e.g. fpg_init, hba1c_init) are never near zero, so skip them there and
    # let the axes frame the actual data range instead.
    if x == "dose_mg" or x.endswith("_delta"):
        ax.axvline(x=0, color="black", linestyle="--", linewidth=1)
    if y == "dose_mg" or y.endswith("_delta"):
        ax.axhline(y=0, color="black", linestyle="--", linewidth=1)

    for _, row in df.iterrows():
        color = "grey" if row["dose_mg"] == 0 else cmap(norm(min(row["dose_mg"], 2.00)))
        marker = MARKERS[row["health"]]
        ax.scatter(
            row[x],
            row[y],
            c=[color],
            marker=marker,
            s=n_to_size(row["n"], n_min, n_max),
            edgecolors="k",
            linewidths=0.5,
            zorder=3,
        )
        xerr = row[f"{x}_{error_key}"] if pd.notna(row[f"{x}_{error_key}"]) else None
        yerr = row[f"{y}_{error_key}"] if pd.notna(row[f"{y}_{error_key}"]) else None
        if xerr is not None or yerr is not None:
            ax.errorbar(
                row[x],
                row[y],
                xerr=xerr,
                yerr=yerr,
                fmt="none",
                ecolor=color,
                elinewidth=0.8,
                capsize=3,
                zorder=2,
            )
        if annotate_points:
            ax.annotate(
                f"{row['study']}\n({row['intervention']})",
                xy=(row[x], row[y]),
                xytext=(3, 3),
                textcoords="offset points",
                fontsize=5.5,
                ha="left",
                va="bottom",
            )

    same_endpoint = (
        x.split("_")[0] == y.split("_")[0]
        and x.split("_")[1] != "delta"
        and y.split("_")[1] != "delta"
    )

    if same_endpoint:
        all_vals = pd.concat([df[x], df[y]])
        lim = (all_vals.min() - 0.5, all_vals.max() + 0.5)
        ax.plot(lim, lim, "k--", lw=1, alpha=0.6, zorder=1)
        ax.set_xlim(lim)
        ax.set_ylim(lim)

    if x in AXIS_LIMITS:
        ax.set_xlim(AXIS_LIMITS[x])
    if y in AXIS_LIMITS:
        ax.set_ylim(AXIS_LIMITS[y])

    x_label = _label_with_unit(x)
    y_label = _label_with_unit(y)

    ax.set_xlabel(x_label, fontsize=12, fontweight="bold")
    ax.set_ylabel(y_label, fontsize=12, fontweight="bold")
    # ax.set_title(f"{x_label} vs {y_label}", fontsize=10)
    # ax.grid(True, alpha=0.25)

    if same_endpoint:
        ax.legend(
            handles=[
                Line2D(
                    [0], [0], linestyle="--", color="k", alpha=0.6, label="no change"
                )
            ],
            loc="upper left",
            fontsize=9,
        )


def dose_norm(df: pd.DataFrame) -> mcolors.Normalize:
    """Normalize the doses above zero to the color scale, up to 2 mg."""
    nonzero_doses = [d for d in df["dose_mg"].unique() if d > 0]
    return mcolors.Normalize(vmin=min(nonzero_doses), vmax=2.00)


def plot_scatter(
    df: pd.DataFrame,
    output_dir: Path,
    x: str,
    y: str,
    error_key: str = "sd",
    weighted_fit: bool = False,
    fit_intercept: bool = False,
) -> None:
    """Scatter: initial FPG (x) vs lowest FPG achieved (y).

    Parameters
    ----------
    df: pd.DataFrame
        pandas DataFrame generated from data_preprocessing.py
    x, y: str ("fpg_init", "fpg_low", "hba1c_init", "hba1c_low", "bw_init", "bw_low")
        string argument that indicates each axis data type
    weighted_fit: bool
        if True, fit and draw a weighted linear regression of `y` ~ `x`
        (see fit_curves.fit_weighted_linear_regression)
    fit_intercept: bool
        if True, fit y = m*x + c (with intercept c). If False (default),
        fit the zero-intercept model y = m*x. Only used when weighted_fit=True.
    """
    n_min, n_max = df["n"].min(), df["n"].max()

    fit = None
    if weighted_fit:
        fit = fit_weighted_linear_regression(
            df, x, y, plot=False, fit_intercept=fit_intercept
        )
        m, m_se = fit.params[0], fit.bse[0]
        if fit_intercept:
            c, c_se = fit.params[1], fit.bse[1]
            console.print(
                f"[weighted fit] {y} = {m:.4g} (+/- {m_se:.4g}) * {x} "
                f"+ {c:.4g} (+/- {c_se:.4g})   (tau^2 = {fit.tau2:.4g})"
            )
        else:
            console.print(
                f"[weighted fit] {y} = {m:.4g} (+/- {m_se:.4g}) * {x}   "
                f"(tau^2 = {fit.tau2:.4g})"
            )

    df = _prepare_pair_df(df, x, y, error_key=error_key)
    console.print(df.to_string())

    norm = dose_norm(df)
    cmap = plt.cm.viridis

    fig, ax = plt.subplots(figsize=(11, 9))
    scatter_on_ax(ax, df, x, y, norm, cmap, n_min, n_max, error_key=error_key)
    # ax.set_title(
    #     f"{_label_with_unit(x)} vs {_label_with_unit(y)} across dulaglutide studies",
    #     fontsize=12,
    # )

    if fit is not None:
        xeval = np.linspace(df[x].min(), df[x].max(), 100)
        fit_func = linear_func_intercept if fit_intercept else linear_func
        yeval = fit_func(xeval, *fit.params)
        ax.plot(xeval, yeval, color="tab:red", lw=2, zorder=4, label="weighted fit")

    # Colorbar for dose
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.01, extend="max")
    # the gradient as vector cells: matplotlib rasterizes it into an
    # embedded image, which some SVG viewers do not show; the edges of
    # the cells in their color close the seams between them
    if cbar.solids is not None:
        cbar.solids.set_rasterized(False)
        cbar.solids.set_edgecolor("face")
    cbar.set_label("Dulaglutide dose (mg)", fontsize=11)

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="gray",
            markeredgecolor="k",
            markersize=9,
            label="T2DM",
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            color="w",
            markerfacecolor="gray",
            markeredgecolor="k",
            markersize=9,
            label="Healthy",
        ),
    ]
    if fit is not None:
        legend_elements.append(
            Line2D([0], [0], color="tab:red", lw=2, label="weighted fit")
        )
    ax.legend(handles=legend_elements, loc="upper left", fontsize=10)

    fig.tight_layout()

    out_path = output_dir / f"{x}_vs_{y}_scatter.png"
    fig.savefig(out_path, dpi=150)
    plt.show()
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_scatter_grid(
    df: pd.DataFrame,
    output_dir: Path,
    pairs: list[tuple[str, str]],
    ncols: int = 3,
    filename: str = "scatter_grid.png",
    dose_fits: dict[str, np.ndarray] | None = None,
    weighted_dose_fits: dict[str, np.ndarray] | None = None,
    delta_fits: dict[tuple[str, str], np.ndarray] | None = None,
    weighted_delta_fits: dict[tuple[str, str], np.ndarray] | None = None,
    error_key: str = "sd",
) -> None:
    """Lay out multiple (x, y) scatter panels on a shared figure.

    Parameters
    ----------
    df: pd.DataFrame
        pandas DataFrame generated from data_preprocessing.py
    pairs: list of (x, y) tuples
        panels are placed row-major into a grid with `ncols` columns,
        e.g. for a 2x3 grid pass the first 3 pairs for row 1 and the
        next 3 for row 2
    dose_fits: dict mapping a y-variable (e.g. "fpg_delta") to the (v, k)
        popt from fit_curves.fit_dose_dependency; drawn as a saturation
        curve on any panel with x == "dose_mg"
    weighted_dose_fits: dict mapping of dose_fits with weighted regression
    delta_fits: dict mapping an (x, y) pair (e.g. ("fpg_delta", "hba1c_delta"))
        to the (m,) popt from fit_curves.fit_linear_dependency; drawn as a
        zero-intercept regression line on the matching panel
    weighted_delta_fits: dict mapping of delta_fits with weighted regression
    """
    nrows = -(-len(pairs) // ncols)  # ceil div
    cmap = plt.cm.viridis
    norm = dose_norm(df)
    n_min, n_max = df["n"].min(), df["n"].max()

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(6 * ncols, 5.5 * nrows), constrained_layout=True
    )
    axes = axes.reshape(nrows, ncols)

    for idx, (x, y) in enumerate(pairs):
        ax = axes[idx // ncols, idx % ncols]
        pair_df = _prepare_pair_df(df, x, y, error_key=error_key)
        # scatter plot
        scatter_on_ax(
            ax,
            pair_df,
            x,
            y,
            norm,
            cmap,
            n_min,
            n_max,
            annotate_points=False,
            error_key=error_key,
        )
        # ax.xaxis.set_major_locator(mticker.MultipleLocator(1.0))
        # ax.yaxis.set_major_locator(mticker.MultipleLocator(0.5))

        if x == "dose_mg" and (dose_fits or weighted_dose_fits):
            xeval = np.linspace(0, pair_df[x].max(), 100)
            if dose_fits and y in dose_fits:
                yeval = saturation_func(xeval, *dose_fits[y])
                ax.plot(xeval, yeval, color="black", lw=2, zorder=4, label="fit")
            if weighted_dose_fits and y in weighted_dose_fits:
                yeval = saturation_func(xeval, *weighted_dose_fits[y])
                ax.plot(
                    xeval,
                    yeval,
                    color="tab:red",
                    lw=2,
                    zorder=4,
                    label="weighted fit",
                )
            ax.legend(fontsize=9, loc="lower left")
        elif (delta_fits and (x, y) in delta_fits) or (
            weighted_delta_fits and (x, y) in weighted_delta_fits
        ):
            xmin = min(0, pair_df[x].min())
            xmax = max(0, pair_df[x].max())
            xeval = np.linspace(xmin, xmax, 100)
            if delta_fits and (x, y) in delta_fits:
                yeval = linear_func(xeval, *delta_fits[(x, y)])
                ax.plot(xeval, yeval, color="black", lw=2, zorder=4, label="fit")
            if weighted_delta_fits and (x, y) in weighted_delta_fits:
                yeval = linear_func(xeval, *weighted_delta_fits[(x, y)])
                ax.plot(
                    xeval,
                    yeval,
                    color="tab:red",
                    lw=2,
                    zorder=4,
                    label="weighted fit",
                )
            ax.legend(fontsize=9, loc="lower left")

    for idx in range(len(pairs), nrows * ncols):
        axes[idx // ncols, idx % ncols].axis("off")

    # Healthy/T2DM
    # legend_elements = [
    #     Line2D(
    #         [0],
    #         [0],
    #         marker="o",
    #         color="w",
    #         markerfacecolor="gray",
    #         markeredgecolor="k",
    #         markersize=9,
    #         label="T2DM",
    #     ),
    #     Line2D(
    #         [0],
    #         [0],
    #         marker="s",
    #         color="w",
    #         markerfacecolor="gray",
    #         markeredgecolor="k",
    #         markersize=9,
    #         label="Healthy",
    #     ),
    # ]
    # fig.legend(
    #     handles=legend_elements,
    #     loc="outside upper center",
    #     ncol=2,
    #     fontsize=10,
    # )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(
        sm, ax=axes.ravel().tolist(), pad=0.01, extend="max", shrink=0.8
    )
    # the gradient as vector cells: matplotlib rasterizes it into an
    # embedded image, which some SVG viewers do not show; the edges of
    # the cells in their color close the seams between them
    if cbar.solids is not None:
        cbar.solids.set_rasterized(False)
        cbar.solids.set_edgecolor("face")
    cbar.set_label("Dulaglutide dose (mg)", fontsize=11)

    out_path = output_dir / filename
    fig.savefig(out_path, dpi=150)
    plt.show()
    plt.close(fig)
    print(f"Saved: {out_path}")


def save_fpg_change_table(df: pd.DataFrame, output_dir: Path) -> None:
    """Print and save FPG change table (init - lowest) per study/dosage."""
    table = df[
        ["study", "intervention", "health", "dose_mg", "fpg_init", "fpg_low"]
    ].copy()
    table["fpg_change"] = (table["fpg_low"] - table["fpg_init"]).round(2)
    table["fpg_init"] = table["fpg_init"].round(2)
    table["fpg_low"] = table["fpg_low"].round(2)
    table = table.sort_values(["dose_mg", "study", "intervention"]).reset_index(
        drop=True
    )

    table.columns = [
        "Study",
        "Intervention",
        "Health",
        "Dose (mg)",
        "Initial FPG (mM)",
        "FPG lowest (mM)",
        "ΔFPG (mM)",
    ]

    print("\n=== FPG change from baseline (initial - lowest) ===")
    print(table.to_string(index=False))

    csv_path = output_dir / "fpg_change.csv"
    table.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")


if __name__ == "__main__":
    from pkdb_models.models.dulaglutide.baseline_viz.data_preprocessing import (
        build_dataset,
    )
    from pkdb_models.models.dulaglutide.baseline_viz.fit_curves import (
        fit_dose_dependency,
        fit_linear_regression,
        fit_weighted_linear_regression,
        fit_weighted_pd_dose_dependency_function,
    )

    output_dir = Path(__file__).parent / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    df = build_dataset()

    # filter dulaglutide and placebo intervention
    mask_dose = df["intervention"].str.startswith(("DUL", "PLAC"))
    df = df[mask_dose]

    # add dose_mg
    df["dose_mg_sd"] = pd.NA
    df["dose_mg_se"] = pd.NA

    error_key = "se"

    # plot_scatter(df, output_dir, y="hba1c_delta", x="fpg_delta", error_key=error_key)
    plot_scatter(df, output_dir, y="bw_delta", x="fpg_delta", error_key=error_key)
    plot_scatter(df, output_dir, y="bw_low", x="fpg_low", error_key=error_key)
    plot_scatter(df, output_dir, y="bw_delta", x="fpg_low", error_key=error_key)
    plot_scatter(df, output_dir, y="fpg_delta", x="fpg_init", error_key=error_key)

    # dose dependency
    plot_scatter(df, output_dir, y="fpg_delta", x="dose_mg", error_key=error_key)
    plot_scatter(df, output_dir, y="hba1c_delta", x="dose_mg", error_key=error_key)
    plot_scatter(df, output_dir, y="bw_delta", x="dose_mg", error_key=error_key)

    dose_fits = {
        "fpg_delta": fit_dose_dependency(df, "fpg"),
        "hba1c_delta": fit_dose_dependency(df, "hba1c"),
        "bw_delta": fit_dose_dependency(df, "bw"),
    }

    weighted_dose_fits = {
        "fpg_delta": fit_weighted_pd_dose_dependency_function(
            df, "fpg", plot=False
        ).params,
        "hba1c_delta": fit_weighted_pd_dose_dependency_function(
            df, "hba1c", plot=False
        ).params,
        "bw_delta": fit_weighted_pd_dose_dependency_function(
            df, "bw", plot=False
        ).params,
    }

    delta_fits = {
        ("fpg_delta", "hba1c_delta"): fit_linear_regression(
            df, "fpg_delta", "hba1c_delta"
        ),
        ("fpg_delta", "bw_delta"): fit_linear_regression(df, "fpg_delta", "bw_delta"),
        ("hba1c_delta", "bw_delta"): fit_linear_regression(
            df, "hba1c_delta", "bw_delta"
        ),
    }

    weighted_delta_fits = {
        ("fpg_delta", "hba1c_delta"): fit_weighted_linear_regression(
            df, "fpg_delta", "hba1c_delta", plot=False
        ).params,
        ("fpg_delta", "bw_delta"): fit_weighted_linear_regression(
            df, "fpg_delta", "bw_delta", plot=False
        ).params,
        ("hba1c_delta", "bw_delta"): fit_weighted_linear_regression(
            df, "hba1c_delta", "bw_delta", plot=False
        ).params,
    }

    plot_scatter_grid(
        df,
        output_dir,
        pairs=[
            # row 1: dose dependency
            ("dose_mg", "fpg_delta"),
            ("dose_mg", "hba1c_delta"),
            ("dose_mg", "bw_delta"),
            # row 2: cross-endpoint deltas
            ("fpg_delta", "hba1c_delta"),
            ("fpg_delta", "bw_delta"),
            ("hba1c_delta", "bw_delta"),
        ],
        ncols=3,
        filename="delta_scatter_grid.png",
        dose_fits=dose_fits,
        weighted_dose_fits=weighted_dose_fits,
        delta_fits=delta_fits,
        weighted_delta_fits=weighted_delta_fits,
        error_key=error_key,
    )

    plot_scatter(
        df,
        output_dir,
        y="fpg_init",
        x="hba1c_init",
        error_key=error_key,
        weighted_fit=True,
        fit_intercept=True,
    )
