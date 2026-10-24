"""Parameter scans of the dulaglutide model.

The dose and the body weight are scanned after a single subcutaneous dose of
dulaglutide, followed for six weeks (about ten half-lives). The renal and
hepatic function are not scanned: the model has no renal or hepatic mechanism
of the elimination of dulaglutide (protein catabolism). The matplotlib figures
show the timecourses of the scans and the pharmacokinetic parameters of
dulaglutide (`dulaglutide_pk`).

In a run over the draws of the fitted parameters (`run_simulation
pkdb_models.models.dulaglutide --uncertainty`) every point of a scan is
simulated for every draw; the figures draw the median of the draws with the
band of their quantiles. The timecourses draw the bands of the reference and
of the two ends of a scan only, the bands of all points would hide the curves.
"""

from typing import ClassVar, Literal, TypedDict, override

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from pkpdsim.scan import point_band, point_timecourse, scan_dimensions, start_values
from sbmlsim import Q
from sbmlsim.plot.serialization_matplotlib import FigureMPL
from sbmlsim.result import ScanResult
from sbmlsim.simulation import Dimension, Scan, Simulation
from sbmlsim.units import Quantity

from pkdb_models.models.dulaglutide import MODEL
from pkdb_models.models.dulaglutide.dulaglutide_pk import summarize
from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)


class ScanSpec(TypedDict):
    """Definition of a single parameter scan."""

    parameter: str
    #: value of the reference simulation
    default: float
    range: np.ndarray
    scale: Literal["linear", "log"]
    colormap: str
    units: str
    label: str


class DulaglutideParameterScan(DulaglutideSimulationExperiment):
    """Scan the effect of parameters on pharmacokinetics."""

    #: pharmacokinetic parameters of the scans by simulation key, set by
    #: `figures_mpl`
    pk_dfs: dict[str, pd.DataFrame]

    tend = 6 * 7 * 24 * 60  # 6 weeks [min]
    dose_dul = 1.5  # [mg]
    #: the quantiles of the bands of the draws of the fitted parameters
    quantiles = (0.05, 0.95)
    #: the opacity of the bands of the draws of the fitted parameters
    band_alpha = 0.15

    num_points = 10
    scan_map: ClassVar[dict[str, ScanSpec]] = {
        "dose_scan": {
            "parameter": "SCDOSE_dul",
            "default": 1.5,
            "range": np.array([0.1, 0.25, 0.5, 0.75, 1.5, 3.0, 4.5, 6.0, 12.0]),
            "scale": "log",
            "colormap": "seismic_r",
            "units": "mg",
            "label": "dulaglutide dose [mg]",
        },
        "bodyweight_scan": {
            "parameter": "BW0",
            "default": 75.0,
            "range": np.sort(np.append(np.linspace(50, 150, num=num_points), [75])),
            "scale": "linear",
            "colormap": "seismic_r",
            "units": "kg",
            "label": "bodyweight [kg]",
        },
    }

    @override
    def simulations(self) -> dict[str, Scan]:
        scans = {}

        for scan_key, scan_data in self.scan_map.items():
            scans[f"scan_{scan_key}"] = Scan(
                simulation=Simulation(
                    time_unit="min",
                    end=self.tend,
                    preinit_changes={
                        **self.default_changes(),
                        # the dose scan scans the dose itself
                        **(
                            {}
                            if scan_key == "dose_scan"
                            else {"SCDOSE_dul": Q(self.dose_dul, "mg")}
                        ),
                    },
                ),
                dimensions=[
                    Dimension(
                        "dim_scan",
                        values={
                            scan_data["parameter"]: Q(
                                scan_data["range"], scan_data["units"]
                            )
                        },
                    ),
                ],
            )

        return scans

    def _across(self) -> str | None:
        """Get the dimension of the draws of the fitted parameters, `None` without."""
        return None if self.uncertainty is None else self.uncertainty.id

    def _scanned(self, res: ScanResult, parameter_id: str) -> Quantity:
        """Get the values of the scanned parameter at the points of the scan."""
        values = start_values(res, parameter_id)
        across = self._across()
        if across is not None:
            values = values.isel({across: 0})
        return Q(values.values, res.units[parameter_id])

    @override
    def figures_mpl(self) -> dict[str, FigureMPL]:
        # calculate pharmacokinetic parameters
        self.pk_dfs = self.calculate_dulaglutide_pk()

        return {
            **self.figures_mpl_timecourses(),
            **self.figures_mpl_pharmacokinetics(),
        }

    def figures_mpl_timecourses(self) -> dict[str, FigureMPL]:
        """Timecourses of the plasma concentration and the mass balance in the scans."""
        sids = [
            "[Cvep_dul]",
            "SCDEPOT_dul",
            "Abody_dul",
            "Acat_dul",
        ]

        figures = {}

        for scan_key, scan_data in self.scan_map.items():
            values = scan_data["range"]
            rmin, rmax = values[0], values[-1]
            cmap = matplotlib.colormaps[scan_data["colormap"]]

            f, axes = plt.subplots(
                nrows=1,
                ncols=len(sids),
                figsize=(6 * len(sids), 6),
                dpi=150,
                layout="constrained",
            )
            f.suptitle(
                f"Scan {scan_data['label']}",
                fontsize=self.suptitle_font_size,
            )

            res = self.results[f"task_scan_{scan_key}"]
            units = res.units
            across = self._across()
            scandim = scan_dimensions(res, across)[0]
            par_vec = self._scanned(res, scan_data["parameter"])
            time_unit = "day"

            for kcol, sid in enumerate(sids):
                ax: Axes = axes[kcol]
                t_default = default = None

                for k_par, par in enumerate(par_vec):
                    band = None
                    with_band = k_par in (0, len(par_vec.magnitude) - 1) or np.isclose(
                        scan_data["default"], par.magnitude
                    )
                    if across is None:
                        time, values = point_timecourse(res, sid, **{scandim: k_par})
                    else:
                        time, lower, values, upper = point_band(
                            res,
                            sid,
                            across=across,
                            quantiles=self.quantiles,
                            **{scandim: k_par},
                        )
                        if with_band:
                            band = (
                                Q(lower, units[sid]).to(self.units[sid]).magnitude,
                                Q(upper, units[sid]).to(self.units[sid]).magnitude,
                            )
                    t_vec = Q(time, units["time"]).to(time_unit)
                    c_vec = Q(values, units[sid]).to(self.units[sid])

                    if np.isclose(scan_data["default"], par.magnitude):
                        color = "black"
                        t_default, default = t_vec, c_vec
                    else:
                        # red lower values, blue higher values
                        if scan_data["scale"] == "linear":
                            cvalue = (par.magnitude - rmin) / np.abs(rmax - rmin)
                        else:
                            cvalue = (
                                np.log10(par.magnitude) - np.log10(rmin)
                            ) / np.abs(np.log10(rmax) - np.log10(rmin))
                        color = cmap(cvalue)

                    if band is not None:
                        ax.fill_between(
                            t_vec.magnitude,
                            *band,
                            color=color,
                            alpha=self.band_alpha,
                            linewidth=0,
                        )
                    ax.plot(
                        t_vec.magnitude,
                        c_vec.magnitude,
                        color=color,
                        linewidth=2.0,
                        label=f"{par.m:.2f}",
                    )

                # plot the reference line in black on top
                if t_default is not None and default is not None:
                    ax.plot(
                        t_default.magnitude,
                        default.magnitude,
                        color="black",
                        linewidth=2.0,
                        label="__nolabel__",
                    )
                ax.set_xlabel(
                    f"{self.label_time} [{time_unit}]",
                    fontdict=self.font,
                )
                ax.tick_params(axis="x", labelsize=self.tick_font_size)
                ax.tick_params(axis="y", labelsize=self.tick_font_size)

                ax.set_ylabel(
                    f"{self.labels[sid]} [{self.units[sid]}]",
                    fontdict=self.font,
                )
                if kcol == 0:
                    ax.legend()

            figures[f"timecourse__{scan_key}"] = f

        return figures

    def figures_mpl_pharmacokinetics(self) -> dict[str, FigureMPL]:
        """Pharmacokinetic parameters depending on the scanned parameters."""
        figures = {}

        parameters_info = [
            ("dulaglutide", "auc_inf_obs"),
            ("dulaglutide", "cmax"),
            ("dulaglutide", "thalf"),
            ("dulaglutide", "cl_f"),
        ]

        for scan_key, scan_data in self.scan_map.items():
            f, axes = plt.subplots(
                nrows=1,
                ncols=len(parameters_info),
                figsize=(6 * len(parameters_info), 6),
                dpi=150,
                layout="constrained",
            )
            f.suptitle(
                f"Pharmacokinetics {scan_data['label']}",
                fontsize=self.suptitle_font_size,
            )
            axes = axes.flatten()

            sim_key = f"scan_{scan_key}"
            res = self.results[f"task_{sim_key}"]
            # the scanned parameter
            x = self._scanned(res, scan_data["parameter"])

            for k, (substance, pk_key) in enumerate(parameters_info):
                ax: Axes = axes[k]
                ax.axvline(x=scan_data["default"], color="grey", linestyle="--")

                df = self.pk_dfs[sim_key]
                df = df[df.substance == substance]  # get PK for substance
                unit = df[f"{pk_key}_unit"].values[0]
                top = 0.0
                if self._across() is None:
                    y = Q(df[pk_key].to_numpy(), unit).to(self.pk_units[pk_key])
                else:
                    stats = summarize(df, pk_key, self.quantiles)
                    y = Q(stats["median"].to_numpy(), unit).to(self.pk_units[pk_key])
                    upper = (
                        Q(stats["upper"].to_numpy(), unit)
                        .to(self.pk_units[pk_key])
                        .magnitude
                    )
                    top = float(np.nanmax(upper))
                    ax.fill_between(
                        x.magnitude,
                        Q(stats["lower"].to_numpy(), unit)
                        .to(self.pk_units[pk_key])
                        .magnitude,
                        upper,
                        color="tab:blue",
                        alpha=self.band_alpha,
                        linewidth=0,
                    )
                ax.plot(
                    x.magnitude,
                    y.magnitude,
                    marker="o",
                    linestyle="-",
                    color="black",
                    markeredgecolor="black",
                    markerfacecolor="tab:blue",
                    markersize=10,
                    label=f"{pk_key} {substance}",
                )

                ax.set_xlabel(
                    scan_data["label"],
                    fontdict=self.scan_font,
                )
                ax.set_ylabel(
                    f"{self.pk_labels[pk_key]} ({substance}) [{self.pk_units[pk_key]}]",
                    fontdict=self.scan_font,
                )
                ax.set_xscale(scan_data["scale"])
                ax.set_ylim(bottom=0, top=1.1 * max(top, float(np.nanmax(y.magnitude))))
                ax.legend()

            figures[f"pk_{scan_key}"] = f

        return figures


if __name__ == "__main__":
    MODEL.run_experiments(
        DulaglutideParameterScan, output_dir=DulaglutideParameterScan.__name__
    )
