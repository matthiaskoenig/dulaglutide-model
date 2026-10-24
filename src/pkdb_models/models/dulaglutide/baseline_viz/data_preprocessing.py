"""Collect the baseline values and their lowest values of the dulaglutide studies.

The tables are read from the study folders of pkdb_data (DATA_PATH_DULAGLUTIDE).
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pkdb_models.models.dulaglutide import DATA_PATH_DULAGLUTIDE

MR_GLC = 180.16  # g/mol, molecular weight of glucose


def _mg_dl_to_mM(v: float) -> float:
    return v / (MR_GLC / 10)


def study_data_dir(study_name: str) -> list[Path]:
    """Return all .tsv files in the given study subdirectory."""
    study_dir = DATA_PATH_DULAGLUTIDE / study_name
    if not study_dir.exists():
        return []
    return sorted(p for p in study_dir.iterdir() if p.suffix == ".tsv")


def group_count(df: pd.DataFrame, name: str) -> float:
    """Return group_count (number of subjects) for a given group name in a TabGroups df."""
    row = df[df["name"] == name]
    if row.empty:
        return np.nan
    return row.iloc[0]["group_count"]


def tab_lookup(df: pd.DataFrame, name: str, mtype: str) -> tuple[float, float, str]:
    """Return (mean, sd, unit) from a TabGroups df for a given group name and measurement_type."""
    row = df[(df["name"] == name) & (df["measurement_type"] == mtype)]
    if row.empty:
        return np.nan, np.nan, ""
    r = row.iloc[0]
    unit = r["unit"] if "unit" in r.index and pd.notna(r["unit"]) else ""
    return r["mean"], r["sd"], unit


def normalize_fpg_to_mmol(fig_df: pd.DataFrame) -> pd.DataFrame:
    """Convert FPG rows with unit mg/dl to mmol/l in fig data."""
    if fig_df.empty or "unit" not in fig_df.columns:
        return fig_df
    mask = fig_df["label"].str.startswith("fpg", na=False) & (
        fig_df["unit"].str.lower() == "mg/dl"
    )
    if not mask.any():
        return fig_df
    fig_df = fig_df.copy()
    for col in ("mean", "sd", "se"):
        if col in fig_df.columns:
            fig_df.loc[mask, col] = fig_df.loc[mask, col].apply(
                lambda v: _mg_dl_to_mM(v) if pd.notna(v) else v
            )
    fig_df.loc[mask, "unit"] = "mmol/l"
    return fig_df


def lowest_change(
    fig_df: pd.DataFrame, label: str, baseline: float, abs_label: str | None = None
) -> tuple[float, float]:
    """Return lowest value from fig data.

    Tries `label` (change-from-baseline) first: returns (baseline + min_change, sd).
    If not found and `abs_label` is given, falls back to absolute values: returns (min, sd) directly.
    """
    if fig_df.empty:
        return np.nan, np.nan
    rows = fig_df[fig_df["label"] == label]
    if len(rows) == 2 and "time" in rows.columns:
        final_rows = rows[rows["time"] != 0]
        if len(final_rows) == 1:
            idx = final_rows.index[0]
            sd = rows.loc[idx, "sd"] if "sd" in rows.columns else np.nan
            return baseline + rows.loc[idx, "mean"], sd
    if not rows.empty:
        if np.isnan(baseline):
            return np.nan, np.nan
        idx = rows["mean"].idxmin()
        sd = rows.loc[idx, "sd"] if "sd" in rows.columns else np.nan
        return baseline + rows.loc[idx, "mean"], sd
    if abs_label is not None:
        abs_rows = fig_df[fig_df["label"] == abs_label]
        if not abs_rows.empty:
            idx = abs_rows["mean"].idxmin()
            sd = abs_rows.loc[idx, "sd"] if "sd" in abs_rows.columns else np.nan
            return abs_rows.loc[idx, "mean"], sd
    return np.nan, np.nan


def get_se(sd: float, n: float) -> float:
    """Calculate standard error from standard deviation and sample size."""
    if pd.isna(sd) or pd.isna(n):
        return np.nan
    return sd / np.sqrt(n)


def build_dataset() -> pd.DataFrame:
    """Build a combined dataFrame.

    Columns:
    --------
        - study | sid: study name and study ID
        - intervention: study subgroup (e.g., "DUL075, "PLAC")
        - n: number of subjects in the subgroup
        - health: "Healthy" or "T2DM"
        - dose_mg: dose in mg
        - fpg_init | fpg_init_sd | fpg_init_se | fpg_low | fpg_low_sd | fpg_low_se | fpg_delta | fpg_delta_sd | fpg_delta_se: fasting plasma glucose (FPG) values in mM
        - hba1c_init | hba1c_init_sd | hba1c_init_se | hba1c_low | hba1c_low_sd | hba1c_low_se | hba1c_delta | hba1c_delta_sd | hba1c_delta_se: HbA1c values in %
        - bw_init | bw_init_sd | bw_init_se | bw_low | bw_low_sd | bw_low_se | bw_delta | bw_delta_sd | bw_delta_se: body weight values in kg
    """
    study_dir_list = [
        "Barrington2011",
        "Barrington2011a",
        "Blonde2015",
        "Chen2018",
        "Dungan2014",
        "Dungan2016",
        "Gerstein2019",
        "Giorgino2015",
        "Grunberger2012",
        "Liu2025",
        "Morioka2024",
        "Nauck2014",
        "Pratley2018",
        "Terauchi2014",
        "Umpierrez2011",
        "Umpierrez2014",
        "Wang2019",
        "Weinstock2015",
        "Wysham2014",
        "Xu2022",
    ]

    columns = [
        "study",
        "sid",
        "intervention",
        "n",
        "health",
        "dose_mg",  # [0, 1, 2, 3, 4, 5]
        "fpg_init",
        "fpg_init_sd",
        "fpg_init_se",
        "fpg_low",
        "fpg_low_sd",
        "fpg_low_se",
        "fpg_delta",
        "fpg_delta_sd",
        "fpg_delta_se",  # [6-14]
        "hba1c_init",
        "hba1c_init_sd",
        "hba1c_init_se",
        "hba1c_low",
        "hba1c_low_sd",
        "hba1c_low_se",
        "hba1c_delta",
        "hba1c_delta_sd",
        "hba1c_delta_se",  # [15-23]
        "bw_init",
        "bw_init_sd",
        "bw_init_se",
        "bw_low",
        "bw_low_sd",
        "bw_low_se",
        "bw_delta",
        "bw_delta_sd",
        "bw_delta_se",  # [24-32]
    ]

    all_rows = []

    for study in study_dir_list:
        TabGroups_dir = next(
            (p for p in study_data_dir(study) if p.stem.endswith("TabGroups")), None
        )
        TabInterventions_dir = next(
            (p for p in study_data_dir(study) if p.stem.endswith("TabInterventions")),
            None,
        )
        if TabGroups_dir is None or TabInterventions_dir is None:
            continue
        TabGroups = pd.read_csv(TabGroups_dir, sep="\t")
        TabInterventions = pd.read_csv(TabInterventions_dir, sep="\t")

        # Pre-load all fig TSVs once per study
        fig_dfs = []
        for p in study_data_dir(study):
            if p.stem.endswith(("TabGroups", "TabInterventions")):
                continue
            try:
                df = pd.read_csv(p, sep="\t")
                if {"label", "mean"}.issubset(df.columns):
                    fig_dfs.append(df)
            except Exception:
                continue
        fig_df = pd.concat(fig_dfs, ignore_index=True) if fig_dfs else pd.DataFrame()
        fig_df = normalize_fpg_to_mmol(fig_df)

        subgroups = [
            sg for sg in TabGroups["name"].unique() if sg not in ["all", "A", "B"]
        ]
        healthy_row = TabGroups[
            (TabGroups["name"] == "all") & (TabGroups["measurement_type"] == "healthy")
        ]
        health = np.nan
        if not healthy_row.empty:
            health = "Healthy" if healthy_row.iloc[0]["choice"] == "Y" else "T2DM"

        for subgroup in subgroups:
            newrow: list[Any] = [np.nan] * len(columns)
            newrow[0] = study
            newrow[1] = f"{study}_{subgroup}"
            newrow[2] = subgroup
            newrow[3] = group_count(TabGroups, subgroup)
            newrow[4] = health

            # dose_mg from TabInterventions
            ti_row = TabInterventions[TabInterventions["name"] == subgroup]
            if not ti_row.empty:
                newrow[5] = ti_row.iloc[0]["value"]

            # baselines from TabGroups (per subgroup)
            fpg_init, fpg_init_sd, fpg_unit = tab_lookup(
                TabGroups, subgroup, "concentration"
            )
            if fpg_unit.lower() == "mg/dl":
                fpg_init = _mg_dl_to_mM(fpg_init) if pd.notna(fpg_init) else fpg_init
                fpg_init_sd = (
                    _mg_dl_to_mM(fpg_init_sd) if pd.notna(fpg_init_sd) else fpg_init_sd
                )
            hba1c_init, hba1c_init_sd, _ = tab_lookup(TabGroups, subgroup, "hba1c")
            bw_init, bw_init_sd, _ = tab_lookup(TabGroups, subgroup, "weight")

            newrow[6], newrow[7] = fpg_init, fpg_init_sd
            newrow[8] = get_se(newrow[7], newrow[3])

            newrow[9], newrow[10] = lowest_change(
                fig_df, f"fpg_change_{subgroup}", fpg_init, abs_label=f"fpg_{subgroup}"
            )
            newrow[11] = get_se(newrow[10], newrow[3])

            newrow[12] = (
                newrow[9] - newrow[6]
                if pd.notna(newrow[6]) and pd.notna(newrow[9])
                else np.nan
            )
            newrow[13] = (
                np.sqrt(newrow[7] ** 2 + newrow[10] ** 2)
                if pd.notna(newrow[7]) and pd.notna(newrow[10])
                else np.nan
            )
            newrow[14] = get_se(newrow[13], newrow[3])

            newrow[15], newrow[16] = hba1c_init, hba1c_init_sd
            newrow[17] = get_se(newrow[16], newrow[3])

            newrow[18], newrow[19] = lowest_change(
                fig_df, f"hba1c_change_{subgroup}", hba1c_init
            )
            newrow[20] = get_se(newrow[19], newrow[3])

            newrow[21] = (
                newrow[18] - newrow[15]
                if pd.notna(newrow[15]) and pd.notna(newrow[18])
                else np.nan
            )
            newrow[22] = (
                np.sqrt(newrow[16] ** 2 + newrow[19] ** 2)
                if pd.notna(newrow[16]) and pd.notna(newrow[19])
                else np.nan
            )
            newrow[23] = get_se(newrow[22], newrow[3])

            newrow[24], newrow[25] = bw_init, bw_init_sd
            newrow[26] = get_se(newrow[25], newrow[3])

            newrow[27], newrow[28] = lowest_change(
                fig_df,
                f"bodyweight_change_{subgroup}",
                bw_init,
                abs_label=f"bodyweight_{subgroup}",
            )
            newrow[29] = get_se(newrow[28], newrow[3])

            newrow[30] = (
                newrow[27] - newrow[24]
                if pd.notna(newrow[24]) and pd.notna(newrow[27])
                else np.nan
            )
            newrow[31] = (
                np.sqrt(newrow[25] ** 2 + newrow[28] ** 2)
                if pd.notna(newrow[25]) and pd.notna(newrow[28])
                else np.nan
            )
            newrow[32] = get_se(newrow[31], newrow[3])

            all_rows.append(newrow)

    dataset = pd.DataFrame(all_rows, columns=columns)
    dataset.to_csv(Path(__file__).resolve().parent / "baseline.csv", index=False)
    return dataset


if __name__ == "__main__":
    df = build_dataset()
    print(df.to_string())
