#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")
// a table longer than a page continues on the next page, its
// caption above it and its header repeated
#show figure.where(kind: table): set block(breakable: true)
#show figure.where(kind: table): set figure.caption(position: top)

#align(center, text(size: 16pt, weight: "bold")[Dulaglutide PBPK\/PD model: fit PD])

= Methods: Dulaglutide PBPK\/PD model: fit PD

== Parameters and data

8 parameters were optimized: maximal effect of the GLP-1 agonist on the excess FPG (fraction) (#raw("Emax_glp1_fpg")), EC50 of the GLP-1 agonist on the excess FPG (#raw("EC50_glp1_fpg")), rate normalization FPG with GLP-1 agonist (#raw("k_fpg")), trial effect on the excess FPG (fraction) (#raw("f_trial_fpg")), hb degradation rate (#raw("k_hb_deg")), maximal effect of the GLP-1 agonist on the subcutaneous fat (fraction) (#raw("Emax_SAT_glp1")), EC50 for GLP-1 agonist on fat loss (#raw("EC50_SAT_glp1")) and rate of the change of the subcutaneous fat (#raw("k_SAT_glp1")). The parameters of the adopted fit PK\_20261018\_102441\_\_faa2d were fixed at their fitted values.

A fit mapping is a curve of a study, the data and the observable of the model it is compared with. The fit has 112 fit mappings of training data with 525 data points, whose residuals enter the objective; 31 fit mappings of validation data with 184 data points, which were simulated and evaluated with the fitted parameters but not fitted; and 3 fit mappings of outliers with 8 data points, data the fit dropped as not usable, which were evaluated like the validation data so that the decision to drop them can be checked. The fit was set up and run with sbmlsim #cite(<Koenig2026_sbmlsim>).

== Objective function

The parameters were estimated by minimizing the objective function

$ F(arrow(p)) = 1/2 sum_k sum_i rho(w_(i,k) r_(i,k)(arrow(p))^2) $

where $k$ runs over the fit mappings of the training data and $i$ over their data points, $r_(i,k)$ is the residual, $w_(i,k) = w_k w^p_(i,k)$ the weight of the data point and $rho$ the loss function, applied to the squared weighted residual $z = w_(i,k) r_(i,k)^2$. The loss function is linear, $rho(z) = z$, i.e. a standard least squares problem.

The residuals are normalized by the mean $overline(y)_k$ of the data of their curve, which makes curves of different quantities and magnitudes comparable:

$ r_(i,k) = (y_(i,k) - f_k(x_(i,k), arrow(p))) / overline(y)_k $

The weight of curve $k$ is $w_k = n_k / N_k$, the weight $n_k$ of its fit mapping (the weight its fit mapping collection assigns, 1 by default, or, for a collection which uses the weights of its mappings, the weight of the mapping, by default the number of subjects of its data) divided by the number $N_k$ of its data points.

A data point is weighted with the inverse of its coefficient of variation, $w^p_(i,k) = |y_(i,k)| / sigma_(i,k)$, with $sigma_(i,k)$ the standard deviation of the data point, or its standard error for data without a standard deviation. An error of zero is missing, a missing error of a curve with errors is replaced by the largest error of the curve, and the data points of a curve without errors have the weight $w^p_(i,k) = 2$, the weight of a coefficient of variation of 0.5.

== Optimization

The optimizer searched the parameters in log10 space within their bounds; bounds, values and intervals are given in the units of the fit parameters, the units of the table of the parameters.

The objective was minimized in 3 runs with differential evolution #cite(<Storn1997>) of SciPy #cite(<Virtanen2020>) within the bounds of the parameters, with the strategy #raw("best1bin"), a population of 15 times the number of parameters, at most 1000 generations, the relative tolerance 0.01 of convergence, the recombination constant 0.7 and a mutation dithered between 0.5 and 1. The initial population of a run was drawn by latin hypercube sampling #cite(<McKay1979>), with a seed of every run derived from the seed 1234 of the fit. The best member of the final population was polished with the L-BFGS-B method of SciPy.

The convergence of the runs was assessed from the traces of their cost and the waterfall plot of their final costs, and the parameter set with the lowest cost was used.

The models were simulated with libRoadRunner #cite(<Welsh2023>) and its integrator CVODE #cite(<Hindmarsh2005>) with the relative tolerance $10^(-6)$ and the absolute tolerance $10^(-6)$, which for a species in a concentration is multiplied by the initial volume of its compartment, and 18 states of its own. It ran with the variable step size of libRoadRunner, i.e. with an output at every step of the integrator. A data point at the time of a change after the start of a simulation, e.g. a dose or the reset of a collection, was compared with the state before the change, except the first data point of a curve with data at later times, which starts a collection and was compared with the state after the change.

== Goodness of fit

The goodness of fit is given per kind of data (training data, validation data and outliers) by metrics over its $n$ data points with the residuals $e_i = y_i - f(x_i, hat(arrow(p)))$ at the fitted parameters $hat(arrow(p))$, the mean squared error, its root and the root mean squared error normalized by the mean $overline(y)_(k(i))$ of the data of the curve of a point:

$ "MSE" = 1/n sum_(i=1)^n e_i^2, quad "RMSE" = sqrt("MSE"), quad "NRMSE" = sqrt(1/n sum_(i=1)^n (e_i / overline(y)_(k(i)))^2) $

The root mean square of the residuals of the objective, i.e. what the fit minimizes, and the coefficient of determination:

$ "RMSE"_w = sqrt(1/n sum_(i=1)^n rho(w_i r_i^2)), quad R^2 = 1 - (sum_i e_i^2) / (sum_i (y_i - overline(y))^2) $

The predictions of a non-linear model are no linear regression of the data, so $R^2$ can be negative: the prediction is worse than the mean of the data. The information criteria of Akaike #cite(<Akaike1974>) and Schwarz #cite(<Schwarz1978>) with the number $n_p$ of fitted parameters are those of a least squares fit with normally distributed residuals, up to an additive constant, so only differences between models fitted to the same data are meaningful:

$ "AIC" = n ln("MSE") + 2 n_p, quad "BIC" = n ln("MSE") + n_p ln(n) $

The percentage of the data points whose prediction $f_i = f(x_i, hat(arrow(p)))$ lies within twofold of the data is taken over the $n_(+)$ data points with positive data $y_i > 0$ and a positive prediction $f_i > 0$; the others have no ratio and are not counted, and a kind of data without such a point has no percentage:

$ P_2 = 100 / n_(+) abs(\{ i : 1/2 <= f_i / y_i <= 2 \}) $

The goodness of fit plot shows the predictions against the data on logarithmic axes, with the lines of twofold $f = 2y$ and $f = y/2$. The Bland-Altman plot #cite(<Bland1986>) shows the ratio of prediction and data as $d_i = log_10(f_i / y_i)$ against the geometric mean $sqrt(f_i y_i)$ for the data points with positive values, with the bias $overline(d)$ and the limits of agreement $overline(d) plus.minus 1.96 s_d$, with the sample standard deviation $s_d$ of $d_i$, of the training data; they are read as the fold factors $10^(overline(d))$ and $10^(overline(d) plus.minus 1.96 s_d)$.

== Identifiability

The identifiability of the parameters was analysed with the profile likelihood #cite(<Raue2009>) #cite(<Kreutz2013>). The profile of a parameter is the lowest objective with the parameter fixed:

$ "PL"(p_j) = min_(p_(l != j)) F(arrow(p)) $

At every point of a scan the other parameters were re-optimized from the previous point with the least squares optimizer of SciPy with the relative step 0.05. A scan ran from the optimum in both directions in the space of the optimizer, with steps in decades of the parameter, starting at 0.1. A step which raised the objective by more than 0.2 of the distance between the objective at the optimum and the threshold was reduced by the factor 2 and repeated, down to 0.01, and the step after one which raised it by less than that divided by the factor was enlarged by the factor, up to 1. A scan stopped at the threshold, at the bound of the parameter, at a point which failed or after 50 points.

The confidence intervals are the values at which the profile crosses the threshold of the likelihood ratio test

$ F_"thr" = F_"min" + chi^2_alpha ("df") / 2 $

with $F_"min"$ the lowest objective of the fit and of all profiles and $chi^2_alpha ("df")$ the quantile of the $chi^2$ distribution at the confidence level $alpha = 0.95$ with df \= 1 degrees of freedom, i.e. 1.92 above the lowest objective. The threshold has this confidence level if $F$ is the negative log-likelihood of the data up to a constant, i.e. if the weighted residuals are independent and normally distributed with unit variance; otherwise the level is approximate. A crossing is interpolated between two points of the profile, on the logarithm of a parameter on a logarithmic scale. A parameter is identifiable if its profile reaches the threshold within the scan on both sides of the optimum, i.e. its confidence interval is finite; practically non-identifiable towards the lower bound if its profile reaches the threshold above the optimum but not below it within the scan, which ends at the lower bound or after 50 points; practically non-identifiable towards the upper bound if its profile reaches the threshold below the optimum but not above it within the scan, which ends at the upper bound or after 50 points; practically non-identifiable if its profile reaches the threshold on neither side within the scans, which end at the bounds or after 50 points, and is not flat; and structurally non-identifiable if its profile is flat on both sides. A side of a profile is flat if it rises by less than 0.05 of the distance between the lowest objective and the threshold, and a profile with a point which failed or did not converge is not classified. The profile likelihood is preferred over the intervals of the Fisher information, its intervals are invariant under a transformation of the parameters and can be asymmetric #cite(<Wieland2021>).

The Fisher information is the local alternative to the profiles: it is the Gauss-Newton approximation of the curvature of the objective at the optimum, from the Jacobian $J$ of the weighted residuals of the training data with respect to the parameters $arrow(p)$ in the space of the optimizer, computed by central finite differences with the step $h_j = epsilon max(|p_j|, 1), space epsilon = 10^(-6)$ of the parameter $p_j$:

$ I = J^top J, quad "cov" = sigma^2 I^(-1), quad sigma^2 = (2 F) / (n - n_p) $

with the number $n$ of data points of the training data and the number $n_p$ of parameters. The information has rank 8 of 8, the number of its eigenvalues above $10^(-8)$ of the largest one, and the condition number 9580; the covariance of an information of a lower rank is computed with the pseudo-inverse. The Wald intervals are $hat(p)_j plus.minus t_((1+alpha)/2, n-n_p) "SE"_j$ with the standard errors $"SE"_j = sqrt("cov"_(j j))$ at the confidence level $alpha = 0.95$, transformed back into the units of the fit parameters.

== Provenance

The fit PD\_20261019\_103700\_\_c0378 was run on 2026-10-19 08:37:26 UTC with sbmlsim 0.10.0 #cite(<Koenig2026_sbmlsim>), libRoadRunner 2.10.0 #cite(<Welsh2023>), SciPy 1.18.1 #cite(<Virtanen2020>), NumPy 2.5.3 #cite(<Harris2020>) and Python 3.14.4 (seed 1234). The models and data were those of commit #raw("a7d90200465ba23560ee963d70986d203c8b41df") of #raw("/home/mkoenig/git/pkdb_models-dulaglutide"); their SHA-256 checksums are listed in #ref(<tab:checksums:PD_20261019_103700__c0378>). The fit kept the values #raw("DULCAT_k") \= 0.00160903, #raw("Kp_dul") \= 0.0870081, #raw("ftissue_dul") \= 0.0282682, #raw("Ksc_dul") \= $4.81 dot 10^(-4)$ and #raw("Fsc_dul") \= 0.478929 of the model fixed.

#figure(
  table(
  columns: 2,
  align: (left, left,),
  table.header([File], [SHA-256]),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011/.Barrington2011_Fig1.tsv"),
  raw("20176599267d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011/.Barrington2011_Fig2.tsv"),
  raw("798431c8090b..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011/.Barrington2011_Tab1.tsv"),
  raw("3da28f3a8cdc..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011/.Barrington2011_TabGroups.tsv"),
  raw("61afc5ec2f7a..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011/.Barrington2011_TabInterventions.tsv"),
  raw("b758eaf2cf07..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011a/.Barrington2011a_Fig1.tsv"),
  raw("09fa713e7de1..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011a/.Barrington2011a_Fig2.tsv"),
  raw("df6839feea0e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011a/.Barrington2011a_Fig3.tsv"),
  raw("8771df0bebe1..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011a/.Barrington2011a_TabGroups.tsv"),
  raw("7e478c9c801f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Barrington2011a/.Barrington2011a_TabInterventions.tsv"),
  raw("7d9c6e22cb0a..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Blonde2015/.Blonde2015_Fig2a.tsv"),
  raw("d4622077f93a..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Blonde2015/.Blonde2015_Fig2b.tsv"),
  raw("032ee105b6af..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Blonde2015/.Blonde2015_Fig2f.tsv"),
  raw("a82edde842a2..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Blonde2015/.Blonde2015_TabGroups.tsv"),
  raw("1a4626420876..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Blonde2015/.Blonde2015_TabInterventions.tsv"),
  raw("57a4f0f0f29d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Chen2018/.Chen2018_Fig2b.tsv"),
  raw("e5fd14cbaa36..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Chen2018/.Chen2018_Fig2d.tsv"),
  raw("d971be80b426..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Chen2018/.Chen2018_Fig2f.tsv"),
  raw("8a930bd27822..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Chen2018/.Chen2018_TabGroups.tsv"),
  raw("8fbb984726c8..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Chen2018/.Chen2018_TabInterventions.tsv"),
  raw("b678d0d7a3e4..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2014/.Dungan2014_Fig2b.tsv"),
  raw("ea390d6166d4..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2014/.Dungan2014_Fig2f.tsv"),
  raw("cdcd76e6f85f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2014/.Dungan2014_Tab2.tsv"),
  raw("7706661da967..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2014/.Dungan2014_TabGroups.tsv"),
  raw("4645ab15523b..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2014/.Dungan2014_TabInterventions.tsv"),
  raw("689b59ded114..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2016/.Dungan2016_Fig2B.tsv"),
  raw("ae476ac9144c..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2016/.Dungan2016_Fig2D.tsv"),
  raw("7e8d3f39d353..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2016/.Dungan2016_Fig2F.tsv"),
  raw("f604a834bd86..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2016/.Dungan2016_TabGroups.tsv"),
  raw("01050e94d86d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Dungan2016/.Dungan2016_TabInterventions.tsv"),
  raw("1e5b2ecf6f42..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCM/.FDAGBCM_Fig21.tsv"),
  raw("8f92f5065408..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCM/.FDAGBCM_Fig42.tsv"),
  raw("432830781e6e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCM/.FDAGBCM_Tab46.tsv"),
  raw("d91880b0f8db..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCM/.FDAGBCM_TabGroups.tsv"),
  raw("b5769ed331cd..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCM/.FDAGBCM_TabIndividuals.tsv"),
  raw("f2170e3a8033..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCM/.FDAGBCM_TabInterventions.tsv"),
  raw("d07ee46a3cfb..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_Fig34.tsv"),
  raw("1b46a7b09bb5..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_Tab11.tsv"),
  raw("c9c0e85c034b..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_Tab33.tsv"),
  raw("87b87b18ed5c..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_Tab34.tsv"),
  raw("1dbd0e08c5fd..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_Tab35.tsv"),
  raw("8b0d2a59637f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_TabGroups.tsv"),
  raw("71bb1f02817a..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBCN/.FDAGBCN_TabInterventions.tsv"),
  raw("b4fd613fb426..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDO/.FDAGBDO_Fig22.tsv"),
  raw("7f4f61591983..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDO/.FDAGBDO_Fig45.tsv"),
  raw("515d77f4f750..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDO/.FDAGBDO_Tab48.tsv"),
  raw("859fa47c6d6e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDO/.FDAGBDO_Tab49.tsv"),
  raw("eebe319efc5e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDO/.FDAGBDO_TabGroups.tsv"),
  raw("5ec7dfdfefaf..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDO/.FDAGBDO_TabInterventions.tsv"),
  raw("f6ed64016f63..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDR/.FDAGBDR_Fig15.tsv"),
  raw("ffe4af50f67d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDR/.FDAGBDR_Fig32.tsv"),
  raw("4322da8a2afe..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDR/.FDAGBDR_Tab10.tsv"),
  raw("26ae65643f48..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDR/.FDAGBDR_Tab31.tsv"),
  raw("0cef62866325..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDR/.FDAGBDR_TabGroups.tsv"),
  raw("ce78f59397cc..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/FDAGBDR/.FDAGBDR_TabInterventions.tsv"),
  raw("018babac593f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gao2024/.Gao2024_Fig2.tsv"),
  raw("b7191b7c34af..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gao2024/.Gao2024_Tab2.tsv"),
  raw("b4b2664aa260..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gao2024/.Gao2024_Tab3.tsv"),
  raw("0a5d7b49ac60..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gao2024/.Gao2024_TabGroups.tsv"),
  raw("a13a104a1b2f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gao2024/.Gao2024_TabInterventions.tsv"),
  raw("f9f0eef97a37..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gerstein2019/.Gerstein2019_Fig4a.tsv"),
  raw("a2a59f9f392a..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gerstein2019/.Gerstein2019_Fig4b.tsv"),
  raw("94a7ca31df3d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gerstein2019/.Gerstein2019_Fig4c.tsv"),
  raw("2f06fbf4df83..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gerstein2019/.Gerstein2019_Fig4d.tsv"),
  raw("04f4dd8414e4..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gerstein2019/.Gerstein2019_TabGroups.tsv"),
  raw("31234340ecbb..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Gerstein2019/.Gerstein2019_TabInterventions.tsv"),
  raw("3351fe8fd309..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Giorgino2015/.Giorgino2015_Fig2b.tsv"),
  raw("15cb98a0622d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Giorgino2015/.Giorgino2015_Fig2d.tsv"),
  raw("63ee3e9f215e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Giorgino2015/.Giorgino2015_Fig2f.tsv"),
  raw("fe262c512f91..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Giorgino2015/.Giorgino2015_TabGroups.tsv"),
  raw("21c35d0044d6..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Giorgino2015/.Giorgino2015_TabInterventions.tsv"),
  raw("88cbe904b7c1..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Grunberger2012/.Grunberger2012_Fig3ab.tsv"),
  raw("b85b8f3637b0..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Grunberger2012/.Grunberger2012_Fig3d.tsv"),
  raw("785f129af4d7..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Grunberger2012/.Grunberger2012_TabGroups.tsv"),
  raw("bc3642f53dbd..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Grunberger2012/.Grunberger2012_TabInterventions.tsv"),
  raw("1fa3e8174272..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Liu2025/.Liu2025_Fig3.tsv"),
  raw("61233a8b2406..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Liu2025/.Liu2025_Tab2.tsv"),
  raw("21cff5b77e80..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Liu2025/.Liu2025_Tab6.tsv"),
  raw("d8087c723671..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Liu2025/.Liu2025_TabGroups.tsv"),
  raw("c4d2f24be315..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Liu2025/.Liu2025_TabInterventions.tsv"),
  raw("ecc9420ee466..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Morioka2024/.Morioka2024_Fig1.tsv"),
  raw("d3ceec1fd00e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Morioka2024/.Morioka2024_Fig2.tsv"),
  raw("af81b9691c88..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Morioka2024/.Morioka2024_Fig3.tsv"),
  raw("657b2c5c5a0f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Morioka2024/.Morioka2024_TabGroups.tsv"),
  raw("1764ea1e3e19..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Morioka2024/.Morioka2024_TabInterventions.tsv"),
  raw("076e5063bd79..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Nauck2014/.Nauck2014_Fig2b.tsv"),
  raw("ed1fb8a72cc8..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Nauck2014/.Nauck2014_Fig2d.tsv"),
  raw("3a54eceee18f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Nauck2014/.Nauck2014_Fig2e.tsv"),
  raw("51eefc1ce59f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Nauck2014/.Nauck2014_TabGroups.tsv"),
  raw("5710b4229816..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Nauck2014/.Nauck2014_TabInterventions.tsv"),
  raw("e45792cfd1ef..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Pratley2018/.Pratley2018_Fig2a.tsv"),
  raw("1197112fd480..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Pratley2018/.Pratley2018_Fig2c.tsv"),
  raw("561d8bcff847..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Pratley2018/.Pratley2018_Fig2g.tsv"),
  raw("3fd86ea36797..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Pratley2018/.Pratley2018_TabGroups.tsv"),
  raw("cab9507b18a4..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Pratley2018/.Pratley2018_TabInterventions.tsv"),
  raw("c783944be36e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Teraruchi2014/.Teraruchi2014_Fig1b.tsv"),
  raw("ac307c905788..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Teraruchi2014/.Teraruchi2014_Fig1d.tsv"),
  raw("deac7c758644..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Teraruchi2014/.Teraruchi2014_Tab2.tsv"),
  raw("2ca9ac22fc1c..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Teraruchi2014/.Teraruchi2014_TabGroups.tsv"),
  raw("c0b57e510943..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Teraruchi2014/.Teraruchi2014_TabInterventions.tsv"),
  raw("18be784d3ca8..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2011/.Umpierrez2011_Fig2a.tsv"),
  raw("868b6781bcad..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2011/.Umpierrez2011_Fig2b.tsv"),
  raw("54a14d2d6967..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2011/.Umpierrez2011_Fig3.tsv"),
  raw("55126e83087f..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2011/.Umpierrez2011_Fig5.tsv"),
  raw("77829da4a269..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2011/.Umpierrez2011_TabGroups.tsv"),
  raw("e28c868f2c85..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2011/.Umpierrez2011_TabInterventions.tsv"),
  raw("0c9dcc0f001c..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2014/.Umpierrez2014_Fig2a.tsv"),
  raw("c61e2b7e520d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2014/.Umpierrez2014_Fig2b.tsv"),
  raw("e42105b88fd0..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2014/.Umpierrez2014_Fig2d.tsv"),
  raw("f63e30025739..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2014/.Umpierrez2014_Fig2f.tsv"),
  raw("72fc96327a03..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2014/.Umpierrez2014_TabGroups.tsv"),
  raw("93c9e2722961..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Umpierrez2014/.Umpierrez2014_TabInterventions.tsv"),
  raw("2fa22bc84d0b..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wang2019/.Wang2019_Fig2b.tsv"),
  raw("d4c5b18f27be..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wang2019/.Wang2019_Fig2d.tsv"),
  raw("87cbfed38324..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wang2019/.Wang2019_Fig2f.tsv"),
  raw("c9065414eba2..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wang2019/.Wang2019_TabGroups.tsv"),
  raw("9a9eae9857e5..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wang2019/.Wang2019_TabInterventions.tsv"),
  raw("89b8b02610a6..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Weinstock2015/.Weinstock2015_Fig2a.tsv"),
  raw("8d8dd02e55e8..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Weinstock2015/.Weinstock2015_Fig2b.tsv"),
  raw("f694ffafada0..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Weinstock2015/.Weinstock2015_Fig2d.tsv"),
  raw("498aa4ea5d20..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Weinstock2015/.Weinstock2015_Fig2e.tsv"),
  raw("68472152b896..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Weinstock2015/.Weinstock2015_TabGroups.tsv"),
  raw("0b3f1dbebd49..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Weinstock2015/.Weinstock2015_TabInterventions.tsv"),
  raw("5f724b71862b..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wysham2014/.Wysham2014_Fig2a.tsv"),
  raw("3b4f56a34fe6..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wysham2014/.Wysham2014_Fig2b.tsv"),
  raw("e254a530934c..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wysham2014/.Wysham2014_Fig2d.tsv"),
  raw("1dc6478fc989..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wysham2014/.Wysham2014_Fig2f.tsv"),
  raw("fcb0e2add93e..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wysham2014/.Wysham2014_TabGroups.tsv"),
  raw("612203818bbe..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Wysham2014/.Wysham2014_TabInterventions.tsv"),
  raw("c65e0986a04d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_Fig1.tsv"),
  raw("803f3b2df214..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_Fig2.tsv"),
  raw("6d89d7f868c2..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_Fig3.tsv"),
  raw("24624b622386..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_Tab2.tsv"),
  raw("cba84b8464c8..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_Tab4.tsv"),
  raw("6d6cfcd0eaae..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_TabGroups.tsv"),
  raw("76a2c9af3d07..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Xu2022/.Xu2022_TabInterventions.tsv"),
  raw("553ed212059d..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Zhang2023/.Zhang2023_Fig2.tsv"),
  raw("7e6f1424e581..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Zhang2023/.Zhang2023_Tab3.tsv"),
  raw("ada4dad3f25b..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Zhang2023/.Zhang2023_Tab4.tsv"),
  raw("66478386bf01..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Zhang2023/.Zhang2023_TabGroups.tsv"),
  raw("77f60a5d9ca6..."),
  raw("pkdb_models/models/dulaglutide/data/dulaglutide/Zhang2023/.Zhang2023_TabInterventions.tsv"),
  raw("6f4e6dd8dc90..."),
  raw("pkdb_models/models/dulaglutide/models/output/models/dulaglutide_body.xml"),
  raw("8b128f2ffd5c..."),
  ),
  caption: [SHA-256 checksums of the models and data of the fit PD\_20261019\_103700\_\_c0378, their first 12 characters; the full checksums are in the provenance of the result (optimization\_result.json).],
) <tab:checksums:PD_20261019_103700__c0378>

= Results: Dulaglutide PBPK\/PD model: fit PD

== Parameters

#figure(
  table(
  columns: 6,
  align: (left, left, right, left, right, left,),
  table.header([Parameter], [Description], [Value \[95% CI\]], [Unit], [Bounds], [Identifiable]),
  raw("Emax_glp1_fpg"),
  [maximal effect of the GLP-1 agonist on the excess FPG (fraction)],
  [0.614 \[0.509, 0.737\]],
  [dimensionless],
  [\[0.05, 1\]],
  [yes],
  raw("EC50_glp1_fpg"),
  [EC50 of the GLP-1 agonist on the excess FPG],
  [3.4e-07 \[1.39e-07, 6.81e-07\]],
  [mmol\/l],
  [\[1e-08, 0.0001\]],
  [yes],
  raw("k_fpg"),
  [rate normalization FPG with GLP-1 agonist],
  [0.00031 \[0.000138, 0.00188\]],
  [l\/min],
  [\[1e-05, 0.01\]],
  [yes],
  raw("f_trial_fpg"),
  [trial effect on the excess FPG (fraction)],
  [0.0424 \[LB, 0.118\]],
  [dimensionless],
  [\[0.001, 0.5\]],
  [no (LB)],
  raw("k_hb_deg"),
  [hb degradation rate],
  [2.43e-05 \[1.71e-05, 3.41e-05\]],
  [mmol\/min],
  [\[5e-06, 5e-05\]],
  [yes],
  raw("Emax_SAT_glp1"),
  [maximal effect of the GLP-1 agonist on the subcutaneous fat (fraction)],
  [0.204 \[0.101, UB\]],
  [dimensionless],
  [\[0.01, 0.8\]],
  [no (UB)],
  raw("EC50_SAT_glp1"),
  [EC50 for GLP-1 agonist on fat loss],
  [4.25e-07 \[LB, 7.28e-06\]],
  [mmol\/l],
  [\[1e-08, 0.0001\]],
  [no (LB)],
  raw("k_SAT_glp1"),
  [rate of the change of the subcutaneous fat],
  [2.11e-05 \[3.74e-06, UB\]],
  [1\/min],
  [\[5e-07, 0.0001\]],
  [no (UB)],
  ),
  caption: [Parameters of the fit PD\_20261019\_103700\_\_c0378, the parameter set PD\_20261019\_103700\_\_c0378\_0, cost 33.1, with their bounds in the optimization. The 95% confidence intervals are those of the profile likelihood, LB and UB an interval which is open towards the lower or the upper bound, and the Wald intervals of the Fisher information for a parameter without a profile. Identifiable is the classification of the profile: yes, no (LB) or no (UB) if the profile does not reach the threshold towards the lower or the upper bound, no if it reaches it on neither side, structural if it is flat.],
) <tab:parameters:PD_20261019_103700__c0378>

== Data

#figure(
  table(
  columns: 5,
  align: (left, right, right, right, right,),
  table.header([Study], [Training], [Validation], [Outlier], [Total]),
  [Barrington2011a],
  [18 (48)],
  [-],
  [3 (8)],
  [21 (56)],
  [Blonde2015],
  [-],
  [4 (28)],
  [-],
  [4 (28)],
  [Chen2018],
  [6 (26)],
  [-],
  [-],
  [6 (26)],
  [Dungan2014],
  [3 (14)],
  [-],
  [-],
  [3 (14)],
  [Dungan2016],
  [6 (28)],
  [-],
  [-],
  [6 (28)],
  [Gerstein2019],
  [-],
  [4 (26)],
  [-],
  [4 (26)],
  [Giorgino2015],
  [-],
  [6 (64)],
  [-],
  [6 (64)],
  [Grunberger2012],
  [10 (45)],
  [-],
  [-],
  [10 (45)],
  [Liu2025],
  [3 (9)],
  [3 (9)],
  [-],
  [6 (18)],
  [Morioka2024],
  [6 (36)],
  [-],
  [-],
  [6 (36)],
  [Nauck2014],
  [9 (63)],
  [-],
  [-],
  [9 (63)],
  [Pratley2018],
  [6 (42)],
  [-],
  [-],
  [6 (42)],
  [Terauchi2014],
  [12 (44)],
  [-],
  [-],
  [12 (44)],
  [Umpierrez2011],
  [6 (20)],
  [6 (20)],
  [-],
  [12 (40)],
  [Umpierrez2014],
  [6 (40)],
  [-],
  [-],
  [6 (40)],
  [Wang2019],
  [6 (38)],
  [-],
  [-],
  [6 (38)],
  [Weinstock2015],
  [6 (24)],
  [-],
  [-],
  [6 (24)],
  [Wysham2014],
  [5 (32)],
  [4 (25)],
  [-],
  [9 (57)],
  [Xu2022],
  [4 (16)],
  [4 (12)],
  [-],
  [8 (28)],
  [Total],
  [112 (525)],
  [31 (184)],
  [3 (8)],
  [146 (717)],
  ),
  caption: [Data of the fit PD\_20261019\_103700\_\_c0378: the number of fit mappings and, in parentheses, of data points per study and kind. The training data enters the cost, the validation data and the outliers are evaluated only.],
) <tab:data:PD_20261019_103700__c0378>

== Goodness of fit

#figure(
  table(
  columns: 11,
  align: (left, right, right, right, right, right, right, right, right, right, right,),
  table.header([Kind], [n], [cost], [MSE], [RMSE], [NRMSE], [RMSE\_w], [R²], [2-fold \[%\]], [AIC], [BIC]),
  [training],
  [525],
  [33.1],
  [0.148],
  [0.385],
  [0.0347],
  [0.355],
  [1],
  [100.0],
  [-986.9],
  [-952.8],
  [validation],
  [184],
  [-],
  [0.658],
  [0.811],
  [0.0356],
  [0.731],
  [1],
  [100.0],
  [-60.9],
  [-35.2],
  [outlier],
  [8],
  [-],
  [0.42],
  [0.648],
  [0.0703],
  [0.181],
  [1],
  [100.0],
  [9.1],
  [9.7],
  ),
  caption: [Goodness of fit of the fit PD\_20261019\_103700\_\_c0378 per kind of data, the parameter set PD\_20261019\_103700\_\_c0378\_0. The cost is defined on the training data only, 2-fold is the percentage of the data points with a positive value and prediction whose prediction is within twofold of the data.],
) <tab:metrics:PD_20261019_103700__c0378>

== Figures

#figure(
  image("plots/traces.svg", width: 100%),
  caption: [Cost of the optimizers over their steps, fit PD\_20261019\_103700\_\_c0378. The cost of every optimization run over its steps. Runs which end at the same cost found the same optimum; a run which stops much higher is stuck in a local minimum.],
) <fig:traces:PD_20261019_103700__c0378>

#figure(
  image("plots/waterfall.svg", width: 100%),
  caption: [Cost of the optimization runs, ordered, fit PD\_20261019\_103700\_\_c0378. The final cost of the runs, ordered. A flat plateau at the left is the global optimum found repeatedly, which is the evidence that the multistart converged; steps to the right are local minima.],
) <fig:waterfall:PD_20261019_103700__c0378>

#figure(
  image("plots/goodness_of_fit.svg", width: 100%),
  caption: [Prediction against the measured data points, per kind of fit mapping, with the agreement of the training data, the lines of twofold and the metrics of the panel, fit PD\_20261019\_103700\_\_c0378. Within twofold of the data are 525 of the 525 training data points (100.0%), 184 of the 184 validation data points (100.0%) and 8 of the 8 outlier data points (100.0%); only the data points with a positive value and prediction are counted. Prediction against measurement, one point per data point, with a panel per kind of fit mapping. The points scatter around the diagonal when the model describes the data; a systematic deviation from it is a systematic error of the model. The band is the agreement of the training data, i.e. the same band the Bland-Altman plot draws, here as lines parallel to the diagonal. The dark red dotted lines are twofold, prediction \= 2 x measurement and prediction \= measurement \/ 2; the caption states the points between them of every kind. A point which is zero or negative is not drawn on the logarithmic axes and not counted, the title of a panel then states the points drawn of all. The validation panel shows how the fit describes data it was not fitted on, the outlier panel the data the fit dropped. The box of a panel carries its R², its normalized RMSE, the RMSE of the residuals of the cost, its fold errors GMFE and AFE and the percentages of its points within twofold and within two standard deviations of the data.],
) <fig:goodness_of_fit:PD_20261019_103700__c0378>

#figure(
  image("plots/bland_altman.svg", width: 100%),
  caption: [Agreement of prediction and measurement as a ratio, per kind of fit mapping, with the agreement of the training data and the agreement of the panel, fit PD\_20261019\_103700\_\_c0378. The ratio of prediction and measurement over the geometric mean of the two, i.e. the goodness of fit with the diagonal turned into the horizontal. The band is the same, the bias and the limits of agreement #raw("bias ± 1.96 SD") of the training data as fold factors. A bias away from 1 is a systematic over- or underprediction, wide limits are a large scatter, and a trend over the mean is a model which describes the large or the small values better. The box of a panel carries the bias and the SD of its own points as fold factors and the share of them inside the limits of agreement of the training data.],
) <fig:bland_altman:PD_20261019_103700__c0378>

#figure(
  image("plots/profiles.svg", width: 100%),
  caption: [Profile likelihood of every parameter: the cost with the parameter fixed and the other parameters optimized, the threshold of the confidence level and the confidence interval, fit PD\_20261019\_103700\_\_c0378. One profile per parameter. A profile which crosses the dashed threshold on both sides gives a finite confidence interval; one which stays below it up to a bound is practically non-identifiable; a flat profile is structurally non-identifiable, the parameter is compensated by the others.],
) <fig:profiles:PD_20261019_103700__c0378>

== Provenance

#figure(
  table(
  columns: 2,
  align: (left, left,),
  table.header([Item], [Value]),
  [Fit],
  raw("PD_20261019_103700__c0378"),
  [Created],
  [2026-10-19 08:37:26 UTC],
  [Seed],
  [1234],
  [Python],
  [3.14.4],
  [sbmlsim],
  [0.10.0],
  [libRoadRunner],
  [2.10.0],
  [SciPy],
  [1.18.1],
  [NumPy],
  [2.5.3],
  [Repository],
  raw("/home/mkoenig/git/pkdb_models-dulaglutide"),
  [Commit],
  raw("a7d90200465ba23560ee963d70986d203c8b41df"),
  [Uncommitted changes],
  [no],
  ),
  caption: [Provenance of the fit PD\_20261019\_103700\_\_c0378: the versions it ran with and the revision of its models and data; the SHA-256 checksums of the models and data are listed in #ref(<tab:checksums:PD_20261019_103700__c0378>).],
) <tab:provenance:PD_20261019_103700__c0378>

#bibliography("references.bib", style: "references.csl")
