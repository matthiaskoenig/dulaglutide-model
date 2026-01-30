"""Parameter scans dulglutide."""
from typing import Dict

import matplotlib.axes
import matplotlib.cm as cm

import numpy as np
from sbmlsim.simulation import Timecourse, TimecourseSim, ScanSim, Dimension
from sbmlsim.plot.serialization_matplotlib import FigureMPL, MatplotlibFigureSerializer
from sbmlsim.plot.serialization_matplotlib import plt
from sbmlutils.console import console

from pkdb_models.models.dulaglutide.experiments.base_experiment import (
    DulaglutideSimulationExperiment,
)
from pkdb_models.models.dulaglutide.helpers import run_experiments


class DulaglutideParameterScan(DulaglutideSimulationExperiment):
    """Scan the effect of parameters on pharmacokinetics."""

    font = {"weight": "bold", "size": 20}
    tick_font_size = 17

    tend = 10 * 24 * 60
    steps = 2000
    dose_dul = 1.5  # [mg]

    num_points = 10
    scan_map = {
        "hepatic_scan": {
            "parameter": "f_cirrhosis",
            "default": 0.0,
            "range": np.linspace(0, 0.9, num=num_points),
            # "range": np.logspace(-2, 2, num=21),
            "scale": "linear",
            "colormap": "Blues",
            "units": "dimensionless",
            "label": "cirrhosis degree [-]",
        },
        "renal_scan": {
            "parameter": "KI__f_renal_function",
            # "range": np.linspace(0.1, 1.9, num=num_points),
            "default": 1.0,
            "range": np.sort(
                np.append(np.logspace(-1, 1, num=num_points), [1.0])
            ),  # [10^-1=0.1, 10^1=10]
            "scale": "log",
            "colormap": "Greens_r",
            "units": "dimensionless",
            "label": "renal function [-]",
        },
        "dose_scan": {
            "parameter": "SCDOSE_dul",
            "default": 1.5,
            "range": np.sort(
                # np.append(np.linspace(1, 100, num=num_points), [10])
                [0.1, 0.2, 0.3, 0.5, 0.625, 0.75, 1.5, 3, 6, 12]
            ),  # [10^-1=0.1, 10^1=10]
            # "range": np.sort(
            #     np.append(np.logspace(1, 2, num=num_points), [50])
            # ),  # [10^-1=0.1, 10^1=10]
            "scale": "linear",
            "colormap": "Reds",
            "units": "mg",
            "label": "dulaglutide dose [mg]",
        },
        "bodyweight_scan": {
            "parameter": "BW0",
            "default": 75,
            "range": np.sort(
                np.append(np.linspace(60, 140, num=num_points), [75])

            ),  # [10^-1=0.1, 10^1=10]
            # "range": np.sort(
            #     np.append(np.logspace(1, 2, num=num_points), [50])
            # ),  # [10^-1=0.1, 10^1=10]
            "scale": "linear",
            "colormap": "Purples",
            "units": "kg",
            "label": "bodyweight [kg]",
        },
    }

    def simulations(self) -> Dict[str, ScanSim]:
        Q_ = self.Q_
        tcscans = {}

        for scan_key, scan_data in self.scan_map.items():
            tcscans[f"scan_sc_{scan_key}"] = ScanSim(
                simulation=TimecourseSim(
                    Timecourse(
                        start=0,
                        end=self.tend,
                        steps=self.steps,
                        changes={
                            **self.default_changes(),
                            "SCDOSE_dul": Q_(self.dose_dul, "mg"),
                        },
                    )
                ),
                dimensions=[
                    Dimension(
                        "dim_scan",
                        changes={
                            scan_data["parameter"]: Q_(
                                scan_data["range"], scan_data["units"]
                            )
                        },
                    ),
                ],
            )

        return tcscans

    def figures_mpl(self) -> Dict[str, FigureMPL]:
        """Matplotlib figures."""
        # calculate pharmacokinetic parameters
        self.pk_dfs = self.calculate_dulaglutide_pk()
        # self.pd_dfs = self.calculate_rivaroxaban_pd()
        # console.print(self.pd_dfs)

        return {
            **self.figures_mpl_timecourses(),
            **self.figures_mpl_pharmacokinetics(),
            # **self.figures_mpl_pharmacodynamics(),
        }

    def figures_mpl_timecourses(self) -> Dict[str, FigureMPL]:
        """Timecourse plots for key variables depending on variables."""

        figures = {}
        for scan_key, scan_data in self.scan_map.items():
            range = scan_data["range"]
            rmin, rmax = range[0], range[-1]

            # cmap_str
            cmap_str = scan_data["colormap"]
            cmap = matplotlib.colormaps.get_cmap(cmap_str)

            # -----------------------------------
            # pharmacokinetics & pharmacodynamics
            # -----------------------------------
            sids = [
                "[Cve_dul]",
                "[Cve_dm]",
                "Aurine_dm",
                "Afeces_dm",
                "BW_change",
                "hba1c_change",
                "fpg_change",
            ]

            f, axes = plt.subplots(
                nrows=2,
                ncols=4,
                figsize=(6 * 4, 5 * 2),
                dpi=300,
                layout="constrained"
            )

            ymax = {}
            for ksid, sid in enumerate(sids):
                ymax[sid] = 0.0
                ax = axes.flatten()[ksid]

                # get data
                Q_ = self.Q_
                xres = self.results[
                    f"task_scan_sc_{scan_key}"
                ]

                # scanned dimension
                scandim = xres._redop_dims()[0]
                parameter_id = scan_data["parameter"]
                par_vec = Q_(
                    xres[parameter_id].values[0], xres.uinfo[parameter_id]
                )
                t_vec = xres.dim_mean("time").to(self.units["time"])

                for k_par, par in enumerate(par_vec):
                    c_vec = Q_(
                        xres[sid].sel({scandim: k_par}).values,
                        xres.uinfo[sid],
                    ).to(self.units[sid])

                    # update ymax
                    cmax = np.nanmax(c_vec.magnitude)
                    if cmax > ymax[sid]:
                        ymax[sid] = cmax

                    # 0.1 - 1.9
                    linewidth = 2.0
                    if np.isclose(scan_data["default"], par.magnitude):
                        color = "black"
                        t_vec_default = t_vec
                        c_vec_default = c_vec
                    else:
                        # red less function, blue more function
                        if scan_data["scale"] == "linear":
                            cvalue = (par.magnitude - rmin)/np.abs(rmax-rmin)
                        elif scan_data["scale"] == "log":
                            cvalue = (np.log10(par.magnitude) - np.log10(rmin)) / np.abs(np.log10(rmax) - np.log10(rmin))

                        color = cmap(cvalue)

                    ax.plot(
                        t_vec.magnitude,
                        c_vec.magnitude,
                        color=color,
                        linewidth=linewidth,
                    )

                # plot the reference line in black
                ax.plot(
                    t_vec_default.magnitude,
                    c_vec_default.magnitude,
                    color="black",
                    linewidth=2.0,
                )

                ax.set_xlabel(
                    f"{self.label_time} [{self.units['time']}]",
                    fontdict=self.font,
                )
                ax.set_ylabel(
                    f"{self.labels[sid]} [{self.units[sid].replace('dimensionless', '-')}]",
                    fontdict=self.font,
                )
                ax.tick_params(axis="x", labelsize=self.tick_font_size)
                ax.tick_params(axis="y", labelsize=self.tick_font_size)


            # --- colorbar ---
            # 4-tuple of floats rect = (left, bottom, width, height).
            # A new Axes is added with dimensions rect in normalized (0, 1)
            cb_ax = f.add_axes(rect=[0.12, 0.85, 0.07, 0.08])
            cb_ax.set_in_layout(True)

            # colorbar range
            if scan_data["scale"] == "linear":
                norm = matplotlib.colors.Normalize(vmin=rmin, vmax=rmax, clip=False)
            elif scan_data["scale"] == "log":
                norm = matplotlib.colors.LogNorm(vmin=rmin, vmax=rmax, clip=False)

            cbar = f.colorbar(
                cm.ScalarMappable(norm=norm, cmap=cmap_str),
                cax=cb_ax,
                orientation="horizontal",
            )

            # label
            cbar.ax.set_xlabel(
                scan_data["label"], **{"size": 15, "weight": "bold"}
            )
            cbar.ax.axvline(x=scan_data["default"], color="black", linewidth=2)

            # ticks
            ticks = [rmin, rmax]
            if scan_data["default"] not in ticks:
                ticks.append(scan_data["default"])
                ticks = sorted(ticks)
            console.print(ticks)
            cbar.set_ticks(ticks)
            cbar.set_ticklabels(
                ticks, **{"size": 15, "weight": "medium"}
            )

            figures[f"timecourse__pk__{scan_key}"] = f

        return figures

    def figures_mpl_pharmacokinetics(self):
        """Visualize dependency of pharmacokinetics parameters."""
        Q_ = self.Q_
        figures = {}

        parameters_info = {
            "dul": [
                "aucinf",
                "cmax",
                "thalf",
                # "cl",
                # "cl_hepatic",
                # "cl_renal",
                # "cl_fecal",
            ],
            "dm": [
                "aucinf",
                "cmax",
                "thalf",
                # "cl",
                # "cl_hepatic",
                # "cl_renal",
                # "cl_fecal",
            ],
        }
        colors = {
            "dul": "black",
            "dm": "tab:blue",
        }

        for scan_key, scan_data in self.scan_map.items():
            parameters = parameters_info["dul"]
            f, axes = plt.subplots(
                nrows=1, ncols=len(parameters), figsize=(6 * len(parameters), 5), dpi=300,
                layout="constrained"
            )
            # f.suptitle(
            #     f"{names[substance]}",
            #     fontsize=self.suptitle_font_size,
            # )
            axes = axes.flatten()

            for substance, parameters in parameters_info.items():
                for k, pk_key in enumerate(parameters):
                    ax = axes[k]
                    ax.axvline(x=scan_data["default"], color="grey", linestyle="--")

                    ymax = 0.0

                    sim_key = f"scan_sc_{scan_key}"
                    xres = self.results[f"task_{sim_key}"]
                    df = self.pk_dfs[sim_key]
                    df = df[df.substance == substance]  # get PK for substance

                    # This was scanned
                    parameter_id = scan_data["parameter"]
                    x_vec = Q_(
                        xres[parameter_id].values[0], xres.uinfo[parameter_id]
                    )

                    pk_vec = df[f"{pk_key}"]
                    pk_vec = pk_vec.to_numpy()

                    x = x_vec
                    y = Q_(pk_vec, df[f"{pk_key}_unit"].values[0])

                    y = y.to(self.pk_units[pk_key])
                    ax.plot(
                        x,
                        y,
                        marker="o",
                        linestyle="-",
                        linewidth=2.0,
                        color=colors[substance],
                        markeredgecolor=colors[substance],
                        markeredgewidth=2.0,
                        markerfacecolor="white",
                        markersize=9,
                        label=f"{substance}",
                    )
                    ymax_value = np.nanmax(y.magnitude)
                    if ymax_value > ymax:
                        ymax = ymax_value


                    # ax.set_xlabel(scan_data["label"], fontdict=EnalaprilSimulationExperiment.scan_font)
                    ax.set_xlabel(
                        scan_data["label"],
                        fontdict=self.font,
                    )
                    ax.set_ylabel(
                        f"{self.pk_labels[pk_key]} [{self.pk_units[pk_key]}]",
                        fontdict=self.font,
                    )
                    ax.tick_params(
                        axis="x", labelsize=self.tick_font_size
                    )
                    ax.tick_params(
                        axis="y", labelsize=self.tick_font_size
                    )

                    # set axis
                    # ax.set_ylim(bottom=0.0, top=1.05 * ymax)
                    # ax.set_ylim(bottom=0.0)
                    ax.set_xscale("log")
                    ax.legend(fontsize=DulaglutideSimulationExperiment.legend_font_size)


            figures[f"pk_{scan_key}"] = f
        return figures

    # def figures_mpl_pharmacodynamics(self):
    #     """Visualize dependency of pharmacodynamic parameters."""
    #     Q_ = self.Q_
    #     figures = {}
    #
    #     parameters = {
    #         "PT": "max",
    #         "aPTT": "max",
    #         "Xa_inhibition": "max",
    #     }
    #
    #     for scan_key, scan_data in self.scan_map.items():
    #
    #         f, axes = plt.subplots(
    #             nrows=1, ncols=3, figsize=(6 * 3, 5), dpi=300,
    #             layout="constrained"
    #         )
    #         axes = axes.flatten()
    #
    #         for k, sid in enumerate(parameters):
    #             pd_key = parameters[sid]
    #
    #             if sid == "DBP":
    #                 k = 3
    #             ax = axes[k]
    #             ax.axvline(x=scan_data["default"], color="grey", linestyle="--")
    #
    #             ymax = 0.0
    #
    #             sim_key = f"scan_sc_{scan_key}"
    #             xres = self.results[f"task_{sim_key}"]
    #             dfs = self.pd_dfs[sim_key]
    #             df = dfs[sid]  # get PD for sid
    #
    #             # This was scanned
    #             parameter_id = scan_data["parameter"]
    #             x_vec = Q_(
    #                 xres[parameter_id].values[0], xres.uinfo[parameter_id]
    #             )
    #             pd_vec = df[f"{pd_key}"]
    #             pd_vec = pd_vec.to_numpy()
    #
    #             x = x_vec
    #             y = Q_(pd_vec, df[f"unit"].values[0])
    #
    #             y = y.to(self.units[sid])
    #             ax.plot(
    #                 x,
    #                 y,
    #                 marker="o",
    #                 linestyle="-",
    #                 linewidth=2.0,
    #                 color="black",
    #                 markeredgecolor="black",
    #                 markeredgewidth=2.0,
    #                 markerfacecolor="white",
    #                 markersize=9,
    #             )
    #             ymax_value = np.nanmax(y.magnitude)
    #             if ymax_value > ymax:
    #                 ymax = ymax_value
    #
    #
    #             # ax.set_xlabel(scan_data["label"], fontdict=EnalaprilSimulationExperiment.scan_font)
    #             ax.set_xlabel(
    #                 scan_data["label"],
    #                 fontdict=self.font,
    #             )
    #             ax.set_ylabel(
    #                 f"{pd_key} {self.labels[sid]} [{self.units[sid].replace('dimensionless', '-')}]",
    #                 fontdict=self.font,
    #             )
    #
    #             ax.tick_params(
    #                 axis="x", labelsize=self.tick_font_size
    #             )
    #             ax.tick_params(
    #                 axis="y", labelsize=self.tick_font_size
    #             )
    #
    #             # set axis
    #             # ax.set_ylim(bottom=0.0, top=1.05 * ymax)
    #             # ax.set_ylim(bottom=0.0)
    #             ax.set_xscale("log")
    #             # ax.legend(fontsize=RivaroxabanSimulationExperiment.legend_font_size)
    #
    #         figures[f"pd_{scan_key}"] = f
    #     return figures


if __name__ == "__main__":
    run_experiments(DulaglutideParameterScan, output_dir=DulaglutideParameterScan.__name__)
