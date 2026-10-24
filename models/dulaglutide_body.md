# Dulaglutide body model

Model `dulaglutide_body`, SBML Level 3 Version 2, read from dulaglutide\_body.xml, written by sbmlode 0.3.0.

Dulaglutide body model

Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of dulaglutide in human.

Dulaglutide (59.7 kDa, a dimeric GLP-1 analogue fused to an IgG4 Fc fragment) is given subcutaneously: the dose enters a depot, from which the fraction Fsc\_dul (the absolute bioavailability, 44 % after 1.5 mg) is absorbed into the venous plasma and the rest is degraded at the injection site (sc\_deg\_dul). An intravenous dose or infusion enters the venous plasma. Dulaglutide distributes from the plasma into the interstitial space of the tissues (ftissue\_dul, Kp\_dul) and is eliminated by protein catabolism (DULCAT, a plasma clearance which scales with the body weight). The intact protein is not excreted in the urine or the bile (FDA clinical pharmacology review BLA 125469). The amounts degraded at the injection site (Asc\_deg\_dul) and catabolized (Acat\_dul) close the mass balance.

The fasting plasma glucose, the HbA1c and the body weight respond to the dulaglutide plasma concentration glp1.

The content of this model has been carefully created in a manual research effort.

Terms of use

Copyright © 2026 Matthias König.

This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.

Redistribution and use of any part of this model, with or without modification, are permitted provided that the following conditions are met:

Redistributions of this SBML file must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in a different form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

This model is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

## Units

| Time | Substance | Extent | Volume | Area | Length |
| --- | --- | --- | --- | --- | --- |
| min | mmol | mmol | l | m<sup>2</sup> | m |

## Compartments

| Symbol | Id | Name | Size | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $\mathrm{Vext}$ | `Vext` | plasma | $1.5$ | l | ✓ |
| $\mathrm{Vki}$ | `Vki` | kidney |  | l |  |
| $\mathrm{Vli}$ | `Vli` | liver |  | l |  |
| $\mathrm{Vlu}$ | `Vlu` | lung |  | l |  |
| $\mathrm{Vad}$ | `Vad` | adipose |  | l |  |
| $\mathrm{Vgu}$ | `Vgu` | gut |  | l |  |
| $\mathrm{Vre}$ | `Vre` | rest |  | l |  |
| $\mathrm{Var}$ | `Var` | arterial blood |  | l |  |
| $\mathrm{Vve}$ | `Vve` | venous blood |  | l |  |
| $\mathrm{Vpo}$ | `Vpo` | portal vein |  | l |  |
| $\mathrm{Vhv}$ | `Vhv` | hepatic vein |  | l |  |
| $\mathrm{Vdeg}$ | `Vdeg` | catabolism products | $1$ | l | ✓ |
| $\mathrm{Vki}_{\mathrm{tissue}}$ | `Vki_tissue` | ki tissue |  | l |  |
| $\mathrm{Vki}_{\mathrm{plasma}}$ | `Vki_plasma` | ki plasma |  | l |  |
| $\mathrm{Vli}_{\mathrm{tissue}}$ | `Vli_tissue` | li tissue |  | l |  |
| $\mathrm{Vli}_{\mathrm{plasma}}$ | `Vli_plasma` | li plasma |  | l |  |
| $\mathrm{Vlu}_{\mathrm{tissue}}$ | `Vlu_tissue` | lu tissue |  | l |  |
| $\mathrm{Vlu}_{\mathrm{plasma}}$ | `Vlu_plasma` | lu plasma |  | l |  |
| $\mathrm{Vad}_{\mathrm{tissue}}$ | `Vad_tissue` | ad tissue |  | l |  |
| $\mathrm{Vad}_{\mathrm{plasma}}$ | `Vad_plasma` | ad plasma |  | l |  |
| $\mathrm{Vgu}_{\mathrm{tissue}}$ | `Vgu_tissue` | gu tissue |  | l |  |
| $\mathrm{Vgu}_{\mathrm{plasma}}$ | `Vgu_plasma` | gu plasma |  | l |  |
| $\mathrm{Vre}_{\mathrm{tissue}}$ | `Vre_tissue` | re tissue |  | l |  |
| $\mathrm{Vre}_{\mathrm{plasma}}$ | `Vre_plasma` | re plasma |  | l |  |

## Species

| Symbol | Id | Name | Compartment | Value | Unit | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathrm{hba1c}$ | `hba1c` | HbA1c | $\mathrm{Vext}$ | $0.05$ | \- | amount |
| $\mathrm{fpg}$ | `fpg` | fasting plasma glucose (FPG) | $\mathrm{Vext}$ |  | mmol/l | concentration |
| $\mathrm{hb}$ | `hb` | Hb total | $\mathrm{Vext}$ | $0.95$ | \- | amount |
| $\mathrm{hb}_{\mathrm{total}}$ | `hb_total` | Hb total | $\mathrm{Vext}$ |  | \- | amount |
| $\mathrm{Cki}_{\mathrm{plasma\_dul}}$ | `Cki_plasma_dul` | dulaglutide (kidney plasma) | $\mathrm{Vki}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cli}_{\mathrm{plasma\_dul}}$ | `Cli_plasma_dul` | dulaglutide (liver plasma) | $\mathrm{Vli}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Clu}_{\mathrm{plasma\_dul}}$ | `Clu_plasma_dul` | dulaglutide (lung plasma) | $\mathrm{Vlu}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cad}_{\mathrm{plasma\_dul}}$ | `Cad_plasma_dul` | dulaglutide (adipose plasma) | $\mathrm{Vad}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cgu}_{\mathrm{plasma\_dul}}$ | `Cgu_plasma_dul` | dulaglutide (gut plasma) | $\mathrm{Vgu}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{plasma\_dul}}$ | `Cre_plasma_dul` | dulaglutide (rest plasma) | $\mathrm{Vre}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Car}_{\mathrm{dul}}$ | `Car_dul` | dulaglutide (arterial blood plasma) | $\mathrm{Var}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cve}_{\mathrm{dul}}$ | `Cve_dul` | dulaglutide (venous blood plasma) | $\mathrm{Vve}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cpo}_{\mathrm{dul}}$ | `Cpo_dul` | dulaglutide (portal vein plasma) | $\mathrm{Vpo}$ | $0$ | mmol/l | concentration |
| $\mathrm{Chv}_{\mathrm{dul}}$ | `Chv_dul` | dulaglutide (hepatic vein plasma) | $\mathrm{Vhv}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cki}_{\mathrm{dul}}$ | `Cki_dul` | dulaglutide (kidney) | $\mathrm{Vki}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cli}_{\mathrm{dul}}$ | `Cli_dul` | dulaglutide (liver) | $\mathrm{Vli}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Clu}_{\mathrm{dul}}$ | `Clu_dul` | dulaglutide (lung) | $\mathrm{Vlu}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cad}_{\mathrm{dul}}$ | `Cad_dul` | dulaglutide (adipose) | $\mathrm{Vad}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cgu}_{\mathrm{dul}}$ | `Cgu_dul` | dulaglutide (gut) | $\mathrm{Vgu}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{dul}}$ | `Cre_dul` | dulaglutide (rest) | $\mathrm{Vre}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cvep}_{\mathrm{dul}}$ | `Cvep_dul` | dulaglutide (venous plasma) | $\mathrm{Vve}$ |  | mmol/l | concentration |
| $\mathrm{Acat}_{\mathrm{dul}}$ | `Acat_dul` | dulaglutide catabolized (amount) | $\mathrm{Vdeg}$ | $0$ | mmol | amount |
| $\mathrm{Asc}_{\mathrm{deg\_dul}}$ | `Asc_deg_dul` | dulaglutide degraded at the injection site (amount) | $\mathrm{Vdeg}$ | $0$ | mmol | amount |

## Parameters

| Symbol | Id | Name | Value | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $\mathrm{BW}_{0}$ | `BW0` | bodyweight | $75$ | kg | ✓ |
| $\mathrm{BW}$ | `BW` | bodyweight |  | kg |  |
| $\mathrm{BW}_{\mathrm{change}}$ | `BW_change` | bodyweight change |  | kg |  |
| $\mathrm{BW}_{\mathrm{ratio}}$ | `BW_ratio` | bodyweight ratio |  | \- |  |
| $\mathrm{BW}_{\mathrm{relchange}}$ | `BW_relchange` | bodyweight relative change |  | \- |  |
| $\mathrm{FAT}$ | `FAT` | additional fat to LBM \[kg\] |  | kg |  |
| $\mathrm{FVad}$ | `FVad` | adipose tissue volume |  | l/kg |  |
| $\mathrm{DSAT}$ | `DSAT` | change in additional fat to LBM \[kg\] | $0$ | kg |  |
| $\mathrm{HEIGHT}$ | `HEIGHT` | height \[cm\] | $170$ | cm | ✓ |
| $\mathrm{SEX}$ | `SEX` | sex | $0$ | \- | ✓ |
| $\mathrm{conversion}_{\mathrm{cm\_per\_m}}$ | `conversion_cm_per_m` | Conversion factor cm to m | $100$ | cm/m | ✓ |
| $\mathrm{Emax}_{\mathrm{SAT\_glp1}}$ | `Emax_SAT_glp1` | maximal effect of the GLP-1 agonist on the subcutaneous fat (fraction) | $0.203821844922692$ | \- | ✓ |
| $\gamma_{\mathrm{SAT\_glp1}}$ | `gamma_SAT_glp1` | gamma for GLP-1 agonist on fat loss | $1$ | \- | ✓ |
| $\mathrm{EC50}_{\mathrm{SAT\_glp1}}$ | `EC50_SAT_glp1` | EC50 for GLP-1 agonist on fat loss | $4.2472499454937 \times 10^{-7}$ | mmol/l | ✓ |
| $k_{\mathrm{SAT\_glp1}}$ | `k_SAT_glp1` | rate of the change of the subcutaneous fat | $2.10876513008034 \times 10^{-5}$ | 1/min | ✓ |
| $\mathrm{cf}_{\mathrm{units\_per\_mmole}}$ | `cf_units_per_mmole` | conversion factor for dimensionless species | $1$ | 1/mmol | ✓ |
| $\mathrm{hba1c0}$ | `hba1c0` | HbA1c | $0.05$ | \- | ✓ |
| $\mathrm{hba1c}_{\mathrm{change}}$ | `hba1c_change` | HbA1c change |  | \- |  |
| $\mathrm{hba1c}_{\mathrm{ratio}}$ | `hba1c_ratio` | HbA1c ratio |  | \- |  |
| $\mathrm{hba1c}_{\mathrm{relchange}}$ | `hba1c_relchange` | HbA1c relative change |  | \- |  |
| $\mathrm{fpg}_{0}$ | `fpg0` | fasting plasma glucose (FPG) | $5$ | mmol/l | ✓ |
| $\mathrm{fpg}_{\mathrm{change}}$ | `fpg_change` | fasting plasma glucose (FPG) change |  | mmol/l |  |
| $\mathrm{fpg}_{\mathrm{ratio}}$ | `fpg_ratio` | fasting plasma glucose (FPG) ratio |  | \- |  |
| $\mathrm{fpg}_{\mathrm{relchange}}$ | `fpg_relchange` | fasting plasma glucose (FPG) relative change |  | \- |  |
| $\mathrm{hb}_{0}$ | `hb0` | Hb (baseline) |  | \- |  |
| $\mathrm{glp}_{1}$ | `glp1` | GLP-1 agonist plasma concentration \[mM\] |  | mmol/l |  |
| $\mathrm{fpg}_{\mathrm{baseline}}$ | `fpg_baseline` | target fasting plasma glucose |  | mmol/l |  |
| $\mathrm{fpg}_{\mathrm{norm}}$ | `fpg_norm` | normal fasting plasma glucose | $5$ | mmol/l | ✓ |
| $k_{\mathrm{fpg}}$ | `k_fpg` | rate normalization FPG with GLP-1 agonist | $0.000310499807261476$ | l/min | ✓ |
| $\mathrm{Emax}_{\mathrm{glp1\_fpg}}$ | `Emax_glp1_fpg` | maximal effect of the GLP-1 agonist on the excess FPG (fraction) | $0.614119779327275$ | \- | ✓ |
| $\mathrm{EC50}_{\mathrm{glp1\_fpg}}$ | `EC50_glp1_fpg` | EC50 of the GLP-1 agonist on the excess FPG | $3.40377712518398 \times 10^{-7}$ | mmol/l | ✓ |
| $f_{\mathrm{trial\_fpg}}$ | `f_trial_fpg` | trial effect on the excess FPG (fraction) | $0.0424121844032083$ | \- | ✓ |
| $k_{\mathrm{hb\_deg}}$ | `k_hb_deg` | hb degradation rate | $2.42752482444634 \times 10^{-5}$ | mmol/min | ✓ |
| $k_{\mathrm{hb\_syn}}$ | `k_hb_syn` | hb synthesis rate |  | mmol/min |  |
| $G_{\mathrm{off\_fpg}}$ | `G_off_fpg` | glucose offset of the glycation | $2.59$ | mmol/l | ✓ |
| $k_{\mathrm{hb\_gly}}$ | `k_hb_gly` | hb glycation rate | $\mathrm{NaN}$ | l/min | ✓ |
| $\mathrm{BW}_{\mathrm{ref}}$ | `BW_ref` | reference body weight \[kg\] | $75$ | kg | ✓ |
| $\mathrm{COBW}$ | `COBW` | cardiac output per bodyweight \[ml/s/kg\] | $1.548$ | ml/s/kg | ✓ |
| $f_{\mathrm{cardiac\_function}}$ | `f_cardiac_function` | heart function | $1$ | \- | ✓ |
| $\mathrm{CO}$ | `CO` | cardiac output \[ml/s\] |  | ml/s |  |
| $\mathrm{QC}$ | `QC` | cardiac output \[l/min\] |  | l/min |  |
| $\mathrm{Fblood}$ | `Fblood` | blood fraction of organ volume | $0.02$ | \- | ✓ |
| $\mathrm{HCT}$ | `HCT` | hematocrit | $0.51$ | \- | ✓ |
| $\mathrm{FVgu}$ | `FVgu` | gut fractional tissue volume | $0.0171$ | l/kg | ✓ |
| $\mathrm{FVki}$ | `FVki` | kidney fractional tissue volume | $0.0044$ | l/kg | ✓ |
| $\mathrm{FVli}$ | `FVli` | liver fractional tissue volume | $0.021$ | l/kg | ✓ |
| $\mathrm{FVlu}$ | `FVlu` | lung fractional tissue volume | $0.0076$ | l/kg | ✓ |
| $\mathrm{FVre}$ | `FVre` | rest of body fractional tissue volume |  | l/kg |  |
| $\mathrm{FVve}$ | `FVve` | venous fractional tissue volume | $0.0514$ | l/kg | ✓ |
| $\mathrm{FVar}$ | `FVar` | arterial fractional tissue volume | $0.0257$ | l/kg | ✓ |
| $\mathrm{FVpo}$ | `FVpo` | portal fractional tissue volume | $0.001$ | l/kg | ✓ |
| $\mathrm{FVhv}$ | `FVhv` | hepatic venous fractional tissue volume | $0.001$ | l/kg | ✓ |
| $\mathrm{FQgu}$ | `FQgu` | gut fractional tissue blood flow | $0.18$ | \- | ✓ |
| $\mathrm{FQki}$ | `FQki` | kidney fractional tissue blood flow | $0.19$ | \- | ✓ |
| $\mathrm{FQh}$ | `FQh` | hepatic (venous side) fractional tissue blood flow | $0.215$ | \- | ✓ |
| $\mathrm{FQad}$ | `FQad` | adipose tissue fractional tissue blood flow | $0.05$ | \- | ✓ |
| $\mathrm{FQlu}$ | `FQlu` | lung fractional tissue blood flow | $1$ | \- | ✓ |
| $\mathrm{FQre}$ | `FQre` | rest of body fractional tissue blood flow |  | \- |  |
| $\mathrm{Mr}_{\mathrm{dul}}$ | `Mr_dul` | Molecular weight dul \[g/mole\] | $59670$ | g/mol | ✓ |
| $\mathrm{BP}_{\mathrm{dul}}$ | `BP_dul` | blood-to-plasma ratio dul |  | \- |  |
| $\mathrm{ftissue}_{\mathrm{dul}}$ | `ftissue_dul` | tissue distribution dul | $0.0282682390316921$ | l/min | ✓ |
| $\mathrm{Kp}_{\mathrm{dul}}$ | `Kp_dul` | tissue/plasma partition coefficient dul | $0.0870081209863143$ | \- | ✓ |
| $\mathrm{Abody}_{\mathrm{dul}}$ | `Abody_dul` | dulaglutide in the body (amount) |  | mmol |  |
| $\mathrm{IVDOSE}_{\mathrm{dul}}$ | `IVDOSE_dul` | IV bolus dose dul \[mg\] | $0$ | mg |  |
| $\mathrm{ti}_{\mathrm{dul}}$ | `ti_dul` | injection time dul \[s\] | $10$ | s | ✓ |
| $\mathrm{Ki}_{\mathrm{dul}}$ | `Ki_dul` | Ki \[1/min\] injection dul |  | 1/min |  |
| $\mathrm{Ri}_{\mathrm{dul}}$ | `Ri_dul` | Ri \[mg/min\] rate of infusion dul | $0$ | mg/min | ✓ |
| $\mathrm{SCDOSE}_{\mathrm{dul}}$ | `SCDOSE_dul` | subcutaneous dose dul \[mg\] | $0$ | mg |  |
| $\mathrm{SCDEPOT}_{\mathrm{dul}}$ | `SCDEPOT_dul` | subcutaneous depot dul \[mg\] | $0$ | mg |  |
| $\mathrm{Ksc}_{\mathrm{injection\_dul}}$ | `Ksc_injection_dul` | subcutaneous injection rate dul | $100$ | 1/min | ✓ |
| $\mathrm{Ksc}_{\mathrm{dul}}$ | `Ksc_dul` | subcutaneous absorption rate dul | $0.000480962525106916$ | 1/min | ✓ |
| $\mathrm{Fsc}_{\mathrm{dul}}$ | `Fsc_dul` | subcutaneous bioavailability dul | $0.478929206680693$ | \- | ✓ |
| $\mathrm{DULCAT}_{\mathrm{k}}$ | `DULCAT_k` | dulaglutide catabolic clearance (blood) | $0.00160903260348705$ | l/min | ✓ |
| $\mathrm{LBW}_{0}$ | `LBW0` |  |  | kg |  |
| $\mathrm{VAT}_{0}$ | `VAT0` |  |  | kg |  |
| $\mathrm{FAT}_{0}$ | `FAT0` |  |  | kg |  |
| $\mathrm{SAT}_{0}$ | `SAT0` |  |  | kg |  |
| $\mathrm{LBW}$ | `LBW` |  |  | kg |  |
| $\mathrm{VAT}$ | `VAT` |  |  | kg |  |
| $\mathrm{SAT}$ | `SAT` |  |  | kg |  |
| $\mathrm{BSA}$ | `BSA` |  |  | m<sup>2</sup> |  |
| $\mathrm{BMI}$ | `BMI` |  |  | kg/m<sup>2</sup> |  |
| $\mathrm{BFF}$ | `BFF` | body fat fraction |  | \- |  |
| $\mathrm{Qgu}$ | `Qgu` | gut blood flow |  | l/min |  |
| $\mathrm{Qki}$ | `Qki` | kidney blood flow |  | l/min |  |
| $\mathrm{Qh}$ | `Qh` | hepatic (venous side) blood flow |  | l/min |  |
| $\mathrm{Qha}$ | `Qha` | hepatic artery blood flow |  | l/min |  |
| $\mathrm{Qlu}$ | `Qlu` | lung blood flow |  | l/min |  |
| $\mathrm{Qad}$ | `Qad` | adipose tissue blood flow |  | l/min |  |
| $\mathrm{Qre}$ | `Qre` | rest of body blood flow |  | l/min |  |
| $\mathrm{Qpo}$ | `Qpo` | portal blood flow |  | l/min |  |

## Initial assignments and assignment rules

The initial assignments set the values at $t = 0$:

$$
\begin{aligned}
\mathrm{hba1c} &= \mathrm{hba1c0} \\[1ex]
\mathrm{fpg} &= \mathrm{fpg}_{0} \\[1ex]
\mathrm{hb} &= 1 - \mathrm{hba1c0} \\[1ex]
k_{\mathrm{hb\_gly}} &= \frac{k_{\mathrm{hb\_deg}} \cdot \mathrm{hba1c0}}{\mathopen{}\left(1 - \mathrm{hba1c0}\right) \cdot \mathopen{}\left(\mathrm{fpg}_{0} + G_{\mathrm{off\_fpg}}\right)}
\end{aligned}
$$

The assignment rules hold at every time $t$:

$$
\begin{aligned}
\mathrm{LBW}_{0} &= \begin{cases} 0.407 \cdot \mathrm{BW}_{0} + 0.267 \cdot \mathrm{HEIGHT} - 19.2 & \text{if } \mathrm{SEX} = 0 \\ 0.252 \cdot \mathrm{BW}_{0} + 0.473 \cdot \mathrm{HEIGHT} - 48.3 & \text{if } \mathrm{SEX} = 1 \\ \mathrm{NaN} & \text{otherwise} \end{cases} \\[1ex]
\mathrm{VAT}_{0} &= \begin{cases} \min\mathopen{}\left(\mathrm{BW}_{0} - \mathrm{LBW}_{0}, 0.2 \cdot \mathrm{LBW}_{0}\right) & \text{if } \mathrm{SEX} = 0 \\ \min\mathopen{}\left(\mathrm{BW}_{0} - \mathrm{LBW}_{0}, 0.1 \cdot \mathrm{LBW}_{0}\right) & \text{if } \mathrm{SEX} = 1 \\ \mathrm{NaN} & \text{otherwise} \end{cases} \\[1ex]
\mathrm{FAT}_{0} &= \mathrm{BW}_{0} - \mathrm{LBW}_{0} \\[1ex]
\mathrm{SAT}_{0} &= \mathrm{FAT}_{0} - \mathrm{VAT}_{0} \\[1ex]
\mathrm{LBW} &= \mathrm{LBW}_{0} \\[1ex]
\mathrm{VAT} &= \mathrm{VAT}_{0} \\[1ex]
\mathrm{SAT} &= \mathrm{SAT}_{0} + \mathrm{DSAT} \\[1ex]
\mathrm{FAT} &= \mathrm{VAT} + \mathrm{SAT} \\[1ex]
\mathrm{BW} &= \mathrm{LBW} + \mathrm{FAT} \\[1ex]
\mathrm{BW}_{\mathrm{change}} &= \mathrm{BW} - \mathrm{BW}_{0} \\[1ex]
\mathrm{BW}_{\mathrm{ratio}} &= \frac{\mathrm{BW}}{\mathrm{BW}_{0}} \\[1ex]
\mathrm{BW}_{\mathrm{relchange}} &= \frac{\mathrm{BW} - \mathrm{BW}_{0}}{\mathrm{BW}_{0}} \\[1ex]
\mathrm{BSA} &= 0.024265 \cdot \mathopen{}\left(\frac{\mathrm{BW}}{1}\right)^{0.5378} \cdot \mathopen{}\left(\frac{\mathrm{HEIGHT}}{1}\right)^{0.3964} \\[1ex]
\mathrm{BMI} &= \frac{\mathrm{BW}}{\frac{\frac{\mathrm{HEIGHT}}{\mathrm{conversion}_{\mathrm{cm\_per\_m}}} \cdot \mathrm{HEIGHT}}{\mathrm{conversion}_{\mathrm{cm\_per\_m}}}} \\[1ex]
\mathrm{FVad} &= \frac{\mathrm{FAT}}{\mathrm{BW}} \cdot 1 \\[1ex]
\mathrm{BFF} &= \frac{\mathrm{FAT}}{\mathrm{BW}} \\[1ex]
\mathrm{hba1c}_{\mathrm{change}} &= \mathrm{hba1c} - \mathrm{hba1c0} \\[1ex]
\mathrm{hba1c}_{\mathrm{ratio}} &= \frac{\mathrm{hba1c}}{\mathrm{hba1c0}} \\[1ex]
\mathrm{hba1c}_{\mathrm{relchange}} &= \frac{\mathrm{hba1c} - \mathrm{hba1c0}}{\mathrm{hba1c0}} \\[1ex]
\mathrm{fpg}_{\mathrm{change}} &= \mathrm{fpg} - \mathrm{fpg}_{0} \\[1ex]
\mathrm{fpg}_{\mathrm{ratio}} &= \frac{\mathrm{fpg}}{\mathrm{fpg}_{0}} \\[1ex]
\mathrm{fpg}_{\mathrm{relchange}} &= \frac{\mathrm{fpg} - \mathrm{fpg}_{0}}{\mathrm{fpg}_{0}} \\[1ex]
\mathrm{hb}_{0} &= 1 - \mathrm{hba1c0} \\[1ex]
\mathrm{hb}_{\mathrm{total}} &= \mathrm{hb} + \mathrm{hba1c} \\[1ex]
k_{\mathrm{hb\_syn}} &= k_{\mathrm{hb\_deg}} \\[1ex]
\mathrm{BP}_{\mathrm{dul}} &= 1 - \mathrm{HCT} \\[1ex]
\mathrm{FVre} &= 1 - \mathrm{FVgu} - \mathrm{FVki} - \mathrm{FVli} \\
&\quad {} - \mathrm{FVlu} - \mathrm{FVad} - \mathrm{FVve} - \mathrm{FVar} \\[1ex]
\mathrm{FQre} &= 1 - \mathrm{FQki} - \mathrm{FQad} - \mathrm{FQh} \\[1ex]
\mathrm{CO} &= f_{\mathrm{cardiac\_function}} \cdot \mathrm{BW} \cdot \mathrm{COBW} \\[1ex]
\mathrm{QC} &= \frac{\mathrm{CO}}{1000} \cdot 60 \\[1ex]
\mathrm{Vgu} &= \mathrm{BW} \cdot \mathrm{FVgu} \\[1ex]
\mathrm{Vki} &= \mathrm{BW} \cdot \mathrm{FVki} \\[1ex]
\mathrm{Vli} &= \mathrm{BW} \cdot \mathrm{FVli} \\[1ex]
\mathrm{Vlu} &= \mathrm{BW} \cdot \mathrm{FVlu} \\[1ex]
\mathrm{Vad} &= \mathrm{BW} \cdot \mathrm{FVad} \\[1ex]
\mathrm{Vre} &= \mathrm{BW} \cdot \mathrm{FVre} \\[1ex]
\mathrm{Vve} &= \mathrm{BW} \cdot \mathrm{FVve} - \frac{\mathrm{FVve}}{\mathrm{FVar} + \mathrm{FVve}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVve} - \mathrm{FVar}\right) \\[1ex]
\mathrm{Var} &= \mathrm{BW} \cdot \mathrm{FVar} - \frac{\mathrm{FVar}}{\mathrm{FVar} + \mathrm{FVve}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVve} - \mathrm{FVar}\right) \\[1ex]
\mathrm{Vpo} &= \mathopen{}\left(1 - \mathrm{HCT}\right) \cdot \mathopen{}\left(\mathrm{BW} \cdot \mathrm{FVpo} - \frac{\mathrm{FVpo}}{\mathrm{FVar} + \mathrm{FVve} + \mathrm{FVpo} + \mathrm{FVhv}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVar} - \mathrm{FVve} - \mathrm{FVpo} - \mathrm{FVhv}\right)\right) \\[1ex]
\mathrm{Vhv} &= \mathopen{}\left(1 - \mathrm{HCT}\right) \cdot \mathopen{}\left(\mathrm{BW} \cdot \mathrm{FVhv} - \frac{\mathrm{FVhv}}{\mathrm{FVar} + \mathrm{FVve} + \mathrm{FVpo} + \mathrm{FVhv}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVar} - \mathrm{FVve} - \mathrm{FVpo} - \mathrm{FVhv}\right)\right) \\[1ex]
\mathrm{Qgu} &= \mathrm{QC} \cdot \mathrm{FQgu} \\[1ex]
\mathrm{Qki} &= \mathrm{QC} \cdot \mathrm{FQki} \\[1ex]
\mathrm{Qh} &= \mathrm{QC} \cdot \mathrm{FQh} \\[1ex]
\mathrm{Qha} &= \mathrm{Qh} - \mathrm{Qgu} \\[1ex]
\mathrm{Qlu} &= \mathrm{QC} \cdot \mathrm{FQlu} \\[1ex]
\mathrm{Qad} &= \mathrm{QC} \cdot \mathrm{FQad} \\[1ex]
\mathrm{Qre} &= \mathrm{QC} \cdot \mathrm{FQre} \\[1ex]
\mathrm{Qpo} &= \mathrm{Qgu} \\[1ex]
\mathrm{Vki}_{\mathrm{plasma}} &= \mathrm{Vki} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vki}_{\mathrm{tissue}} &= \mathrm{Vki} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vli}_{\mathrm{plasma}} &= \mathrm{Vli} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vli}_{\mathrm{tissue}} &= \mathrm{Vli} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vlu}_{\mathrm{plasma}} &= \mathrm{Vlu} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vlu}_{\mathrm{tissue}} &= \mathrm{Vlu} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vad}_{\mathrm{plasma}} &= \mathrm{Vad} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vad}_{\mathrm{tissue}} &= \mathrm{Vad} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vgu}_{\mathrm{plasma}} &= \mathrm{Vgu} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vgu}_{\mathrm{tissue}} &= \mathrm{Vgu} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vre}_{\mathrm{plasma}} &= \mathrm{Vre} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vre}_{\mathrm{tissue}} &= \mathrm{Vre} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Cvep}_{\mathrm{dul}} &= \frac{\mathrm{Cve}_{\mathrm{dul}}}{\mathrm{BP}_{\mathrm{dul}}} \\[1ex]
\mathrm{Abody}_{\mathrm{dul}} &= \mathrm{Car}_{\mathrm{dul}} \cdot \mathrm{Var} + \mathrm{Cve}_{\mathrm{dul}} \cdot \mathrm{Vve} + \mathrm{Cpo}_{\mathrm{dul}} \cdot \mathrm{Vpo} + \mathrm{Chv}_{\mathrm{dul}} \cdot \mathrm{Vhv} \\
&\quad {} + \mathrm{Cki}_{\mathrm{plasma\_dul}} \cdot \mathrm{Vki}_{\mathrm{plasma}} + \mathrm{Cli}_{\mathrm{plasma\_dul}} \cdot \mathrm{Vli}_{\mathrm{plasma}} + \mathrm{Clu}_{\mathrm{plasma\_dul}} \cdot \mathrm{Vlu}_{\mathrm{plasma}} + \mathrm{Cad}_{\mathrm{plasma\_dul}} \cdot \mathrm{Vad}_{\mathrm{plasma}} \\
&\quad {} + \mathrm{Cgu}_{\mathrm{plasma\_dul}} \cdot \mathrm{Vgu}_{\mathrm{plasma}} + \mathrm{Cre}_{\mathrm{plasma\_dul}} \cdot \mathrm{Vre}_{\mathrm{plasma}} + \mathrm{Cki}_{\mathrm{dul}} \cdot \mathrm{Vki}_{\mathrm{tissue}} + \mathrm{Cli}_{\mathrm{dul}} \cdot \mathrm{Vli}_{\mathrm{tissue}} \\
&\quad {} + \mathrm{Clu}_{\mathrm{dul}} \cdot \mathrm{Vlu}_{\mathrm{tissue}} + \mathrm{Cad}_{\mathrm{dul}} \cdot \mathrm{Vad}_{\mathrm{tissue}} + \mathrm{Cgu}_{\mathrm{dul}} \cdot \mathrm{Vgu}_{\mathrm{tissue}} + \mathrm{Cre}_{\mathrm{dul}} \cdot \mathrm{Vre}_{\mathrm{tissue}} \\[1ex]
\mathrm{Ki}_{\mathrm{dul}} &= \frac{0.693}{\mathrm{ti}_{\mathrm{dul}}} \cdot 60 \\[1ex]
\mathrm{glp}_{1} &= \mathrm{Cvep}_{\mathrm{dul}} \\[1ex]
\mathrm{fpg}_{\mathrm{baseline}} &= \mathrm{fpg}_{0} - \max\mathopen{}\left(\mathrm{fpg}_{0} - \mathrm{fpg}_{\mathrm{norm}}, 0\right) \cdot \mathopen{}\left(1 - \mathopen{}\left(1 - f_{\mathrm{trial\_fpg}}\right) \cdot \mathopen{}\left(1 - \frac{\mathrm{Emax}_{\mathrm{glp1\_fpg}} \cdot \mathrm{glp}_{1}}{\mathrm{EC50}_{\mathrm{glp1\_fpg}} + \mathrm{glp}_{1}}\right)\right)
\end{aligned}
$$

## Reactions

| Rate | Id | Name | Equation | Modifiers |
| --- | --- | --- | --- | --- |
| $v_{\mathrm{FPGC}}$ | `FPGC` | fpg change | $\mathrm{fpg} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{HBSYN}}$ | `HBSYN` | HB synthesis | $\varnothing \longrightarrow \mathrm{hb}$ |  |
| $v_{\mathrm{HBDEG}}$ | `HBDEG` | HB degradation | $\mathrm{hb} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{HBA1CDEG}}$ | `HBA1CDEG` | HBA1C degradation | $\mathrm{hba1c} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{HBGLYC}}$ | `HBGLYC` | HB glycation | $\mathrm{hb} \longrightarrow \mathrm{hba1c}$ | $\mathrm{fpg}$ |
| $v_{\mathrm{transport\_ki\_dul}}$ | `transport_ki_dul` | transport dulaglutide | $\mathrm{Cki}_{\mathrm{plasma\_dul}} \rightleftharpoons \mathrm{Cki}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{transport\_li\_dul}}$ | `transport_li_dul` | transport dulaglutide | $\mathrm{Cli}_{\mathrm{plasma\_dul}} \rightleftharpoons \mathrm{Cli}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{transport\_lu\_dul}}$ | `transport_lu_dul` | transport dulaglutide | $\mathrm{Clu}_{\mathrm{plasma\_dul}} \rightleftharpoons \mathrm{Clu}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{transport\_ad\_dul}}$ | `transport_ad_dul` | transport dulaglutide | $\mathrm{Cad}_{\mathrm{plasma\_dul}} \rightleftharpoons \mathrm{Cad}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{transport\_gu\_dul}}$ | `transport_gu_dul` | transport dulaglutide | $\mathrm{Cgu}_{\mathrm{plasma\_dul}} \rightleftharpoons \mathrm{Cgu}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{transport\_re\_dul}}$ | `transport_re_dul` | transport dulaglutide | $\mathrm{Cre}_{\mathrm{plasma\_dul}} \rightleftharpoons \mathrm{Cre}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_ve\_lu\_dul}}$ | `Flow_ve_lu_dul` | inflow lung dulaglutide | $\mathrm{Cve}_{\mathrm{dul}} \longrightarrow \mathrm{Clu}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_lu\_ar\_dul}}$ | `Flow_lu_ar_dul` | outflow lung dulaglutide | $\mathrm{Clu}_{\mathrm{plasma\_dul}} \longrightarrow \mathrm{Car}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_ar\_ki\_dul}}$ | `Flow_ar_ki_dul` | inflow kidney dulaglutide | $\mathrm{Car}_{\mathrm{dul}} \longrightarrow \mathrm{Cki}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_ki\_ve\_dul}}$ | `Flow_ki_ve_dul` | outflow kidney dulaglutide | $\mathrm{Cki}_{\mathrm{plasma\_dul}} \longrightarrow \mathrm{Cve}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_ar\_ad\_dul}}$ | `Flow_ar_ad_dul` | inflow adipose dulaglutide | $\mathrm{Car}_{\mathrm{dul}} \longrightarrow \mathrm{Cad}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_ad\_ve\_dul}}$ | `Flow_ad_ve_dul` | outflow adipose dulaglutide | $\mathrm{Cad}_{\mathrm{plasma\_dul}} \longrightarrow \mathrm{Cve}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_ar\_re\_dul}}$ | `Flow_ar_re_dul` | inflow rest dulaglutide | $\mathrm{Car}_{\mathrm{dul}} \longrightarrow \mathrm{Cre}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_re\_ve\_dul}}$ | `Flow_re_ve_dul` | outflow rest dulaglutide | $\mathrm{Cre}_{\mathrm{plasma\_dul}} \longrightarrow \mathrm{Cve}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_ar\_gu\_dul}}$ | `Flow_ar_gu_dul` | inflow gut dulaglutide | $\mathrm{Car}_{\mathrm{dul}} \longrightarrow \mathrm{Cgu}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_gu\_po\_dul}}$ | `Flow_gu_po_dul` | outflow gut dulaglutide | $\mathrm{Cgu}_{\mathrm{plasma\_dul}} \longrightarrow \mathrm{Cpo}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_arli\_li\_dul}}$ | `Flow_arli_li_dul` | arterial inflow liver dulaglutide | $\mathrm{Car}_{\mathrm{dul}} \longrightarrow \mathrm{Cli}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_po\_li\_dul}}$ | `Flow_po_li_dul` | portal inflow liver dulaglutide | $\mathrm{Cpo}_{\mathrm{dul}} \longrightarrow \mathrm{Cli}_{\mathrm{plasma\_dul}}$ |  |
| $v_{\mathrm{Flow\_li\_hv\_dul}}$ | `Flow_li_hv_dul` | outflow liver dulaglutide | $\mathrm{Cli}_{\mathrm{plasma\_dul}} \longrightarrow \mathrm{Chv}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{Flow\_hv\_ve\_dul}}$ | `Flow_hv_ve_dul` | outflow hepatic vein dulaglutide | $\mathrm{Chv}_{\mathrm{dul}} \longrightarrow \mathrm{Cve}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{DULCAT}}$ | `DULCAT` | dulaglutide catabolism | $\mathrm{Cve}_{\mathrm{dul}} \longrightarrow \mathrm{Acat}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{iv\_dul}}$ | `iv_dul` | iv dulaglutide | $\varnothing \longrightarrow \mathrm{Cve}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{sc\_dul}}$ | `sc_dul` | subcutaneous absorption dulaglutide | $\varnothing \longrightarrow \mathrm{Cve}_{\mathrm{dul}}$ |  |
| $v_{\mathrm{sc\_deg\_dul}}$ | `sc_deg_dul` | subcutaneous degradation dulaglutide | $\varnothing \longrightarrow \mathrm{Asc}_{\mathrm{deg\_dul}}$ |  |

The rates of the reactions are:

$$
\begin{aligned}
v_{\mathrm{FPGC}} &= k_{\mathrm{fpg}} \cdot \mathopen{}\left(\mathrm{fpg} - \mathrm{fpg}_{\mathrm{baseline}}\right) \\[1ex]
v_{\mathrm{HBSYN}} &= k_{\mathrm{hb\_syn}} \\[1ex]
v_{\mathrm{HBDEG}} &= k_{\mathrm{hb\_deg}} \cdot \mathrm{hb} \\[1ex]
v_{\mathrm{HBA1CDEG}} &= k_{\mathrm{hb\_deg}} \cdot \mathrm{hba1c} \\[1ex]
v_{\mathrm{HBGLYC}} &= k_{\mathrm{hb\_gly}} \cdot \mathopen{}\left(\mathrm{fpg} + G_{\mathrm{off\_fpg}}\right) \cdot \mathrm{hb} \\[1ex]
v_{\mathrm{transport\_ki\_dul}} &= \frac{\mathrm{ftissue}_{\mathrm{dul}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cki}_{\mathrm{plasma\_dul}} \cdot \mathrm{Kp}_{\mathrm{dul}} - \mathrm{Cki}_{\mathrm{dul}}\right) \\[1ex]
v_{\mathrm{transport\_li\_dul}} &= \frac{\mathrm{ftissue}_{\mathrm{dul}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cli}_{\mathrm{plasma\_dul}} \cdot \mathrm{Kp}_{\mathrm{dul}} - \mathrm{Cli}_{\mathrm{dul}}\right) \\[1ex]
v_{\mathrm{transport\_lu\_dul}} &= \frac{\mathrm{ftissue}_{\mathrm{dul}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Clu}_{\mathrm{plasma\_dul}} \cdot \mathrm{Kp}_{\mathrm{dul}} - \mathrm{Clu}_{\mathrm{dul}}\right) \\[1ex]
v_{\mathrm{transport\_ad\_dul}} &= \frac{\mathrm{ftissue}_{\mathrm{dul}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cad}_{\mathrm{plasma\_dul}} \cdot \mathrm{Kp}_{\mathrm{dul}} - \mathrm{Cad}_{\mathrm{dul}}\right) \\[1ex]
v_{\mathrm{transport\_gu\_dul}} &= \frac{\mathrm{ftissue}_{\mathrm{dul}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cgu}_{\mathrm{plasma\_dul}} \cdot \mathrm{Kp}_{\mathrm{dul}} - \mathrm{Cgu}_{\mathrm{dul}}\right) \\[1ex]
v_{\mathrm{transport\_re\_dul}} &= \frac{\mathrm{ftissue}_{\mathrm{dul}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cre}_{\mathrm{plasma\_dul}} \cdot \mathrm{Kp}_{\mathrm{dul}} - \mathrm{Cre}_{\mathrm{dul}}\right) \\[1ex]
v_{\mathrm{Flow\_ve\_lu\_dul}} &= \mathrm{Qlu} \cdot \mathrm{Cve}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_lu\_ar\_dul}} &= \mathrm{Qlu} \cdot \mathrm{Clu}_{\mathrm{plasma\_dul}} \\[1ex]
v_{\mathrm{Flow\_ar\_ki\_dul}} &= \mathrm{Qki} \cdot \mathrm{Car}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_ki\_ve\_dul}} &= \mathrm{Qki} \cdot \mathrm{Cki}_{\mathrm{plasma\_dul}} \\[1ex]
v_{\mathrm{Flow\_ar\_ad\_dul}} &= \mathrm{Qad} \cdot \mathrm{Car}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_ad\_ve\_dul}} &= \mathrm{Qad} \cdot \mathrm{Cad}_{\mathrm{plasma\_dul}} \\[1ex]
v_{\mathrm{Flow\_ar\_re\_dul}} &= \mathrm{Qre} \cdot \mathrm{Car}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_re\_ve\_dul}} &= \mathrm{Qre} \cdot \mathrm{Cre}_{\mathrm{plasma\_dul}} \\[1ex]
v_{\mathrm{Flow\_ar\_gu\_dul}} &= \mathrm{Qgu} \cdot \mathrm{Car}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_gu\_po\_dul}} &= \mathrm{Qgu} \cdot \mathrm{Cgu}_{\mathrm{plasma\_dul}} \\[1ex]
v_{\mathrm{Flow\_arli\_li\_dul}} &= \mathrm{Qha} \cdot \mathrm{Car}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_po\_li\_dul}} &= \mathrm{Qpo} \cdot \mathrm{Cpo}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{Flow\_li\_hv\_dul}} &= \mathopen{}\left(\mathrm{Qpo} + \mathrm{Qha}\right) \cdot \mathrm{Cli}_{\mathrm{plasma\_dul}} \\[1ex]
v_{\mathrm{Flow\_hv\_ve\_dul}} &= \mathrm{Qh} \cdot \mathrm{Chv}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{DULCAT}} &= \frac{\mathrm{DULCAT}_{\mathrm{k}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathrm{Cve}_{\mathrm{dul}} \\[1ex]
v_{\mathrm{iv\_dul}} &= \frac{\mathrm{Ki}_{\mathrm{dul}} \cdot \mathrm{IVDOSE}_{\mathrm{dul}}}{\mathrm{Mr}_{\mathrm{dul}}} \\[1ex]
v_{\mathrm{sc\_dul}} &= \frac{\mathrm{Fsc}_{\mathrm{dul}} \cdot \mathrm{Ksc}_{\mathrm{dul}} \cdot \mathrm{SCDEPOT}_{\mathrm{dul}}}{\mathrm{Mr}_{\mathrm{dul}}} \\[1ex]
v_{\mathrm{sc\_deg\_dul}} &= \frac{\mathopen{}\left(1 - \mathrm{Fsc}_{\mathrm{dul}}\right) \cdot \mathrm{Ksc}_{\mathrm{dul}} \cdot \mathrm{SCDEPOT}_{\mathrm{dul}}}{\mathrm{Mr}_{\mathrm{dul}}}
\end{aligned}
$$

## ODE system

The states change in time with the rates of the reactions and the rate rules:

$$
\begin{aligned}
\frac{\mathrm{d} \,\mathrm{hba1c}}{\mathrm{d} t} &= -\mathrm{cf}_{\mathrm{units\_per\_mmole}} \cdot v_{\mathrm{HBA1CDEG}} + \mathrm{cf}_{\mathrm{units\_per\_mmole}} \cdot v_{\mathrm{HBGLYC}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{fpg}}{\mathrm{d} t} &= \frac{-v_{\mathrm{FPGC}}}{\mathrm{Vext}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{hb}}{\mathrm{d} t} &= \mathrm{cf}_{\mathrm{units\_per\_mmole}} \cdot v_{\mathrm{HBSYN}} - \mathrm{cf}_{\mathrm{units\_per\_mmole}} \cdot v_{\mathrm{HBDEG}} - \mathrm{cf}_{\mathrm{units\_per\_mmole}} \cdot v_{\mathrm{HBGLYC}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Acat}_{\mathrm{dul}}}{\mathrm{d} t} &= v_{\mathrm{DULCAT}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Asc}_{\mathrm{deg\_dul}}}{\mathrm{d} t} &= v_{\mathrm{sc\_deg\_dul}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{DSAT}}{\mathrm{d} t} &= k_{\mathrm{SAT\_glp1}} \cdot \mathopen{}\left(\frac{-\mathrm{SAT}_{0} \cdot \mathrm{Emax}_{\mathrm{SAT\_glp1}} \cdot \mathrm{glp}_{1}^{\gamma_{\mathrm{SAT\_glp1}}}}{\mathrm{glp}_{1}^{\gamma_{\mathrm{SAT\_glp1}}} + \mathrm{EC50}_{\mathrm{SAT\_glp1}}^{\gamma_{\mathrm{SAT\_glp1}}}} - \mathrm{DSAT}\right) \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{IVDOSE}_{\mathrm{dul}}}{\mathrm{d} t} &= -v_{\mathrm{iv\_dul}} \cdot \mathrm{Mr}_{\mathrm{dul}} + \mathrm{Ri}_{\mathrm{dul}} \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{SCDOSE}_{\mathrm{dul}}}{\mathrm{d} t} &= -\mathrm{Ksc}_{\mathrm{injection\_dul}} \cdot \mathrm{SCDOSE}_{\mathrm{dul}} \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{SCDEPOT}_{\mathrm{dul}}}{\mathrm{d} t} &= \mathrm{Ksc}_{\mathrm{injection\_dul}} \cdot \mathrm{SCDOSE}_{\mathrm{dul}} - \mathopen{}\left(v_{\mathrm{sc\_dul}} + v_{\mathrm{sc\_deg\_dul}}\right) \cdot \mathrm{Mr}_{\mathrm{dul}} \qquad \text{(rate rule)}
\end{aligned}
$$

## Unsupported constructs

The model uses constructs which the ODE system does not express:

- rate of an assigned size `Vki_plasma`
- rate of an assigned size `Vli_plasma`
- rate of an assigned size `Vlu_plasma`
- rate of an assigned size `Vad_plasma`
- rate of an assigned size `Vgu_plasma`
- rate of an assigned size `Vre_plasma`
- rate of an assigned size `Var`
- rate of an assigned size `Vve`
- rate of an assigned size `Vpo`
- rate of an assigned size `Vhv`
- rate of an assigned size `Vki_tissue`
- rate of an assigned size `Vli_tissue`
- rate of an assigned size `Vlu_tissue`
- rate of an assigned size `Vad_tissue`
- rate of an assigned size `Vgu_tissue`
- rate of an assigned size `Vre_tissue`
