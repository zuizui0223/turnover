# Exact binary state-balance attenuation identity

## Statement

Let the (M) pairwise observations be indexed by (i=1,ldots,M).

- (X_i) is the rank of pairwise phylogenetic distance.
- (Y_iin\{0,1\}) is binary trait mismatch, with (Y_i=1) for a mismatching pair.
- (p=M^{-1}sum_i Y_i) is mismatch-pair prevalence.
- (ar X_1) and (ar X_0) are the mean distance ranks among mismatch and match pairs.
- (sigma_X^2=M^{-1}sum_i(X_i-ar X)^2) is the population-form variance of the distance ranks over the (M) pairwise observations.
- (Delta_{rank}=(ar X_1-ar X_0)/sigma_X).

Then the Pearson correlation of (X) with binary mismatch (Y), and therefore the Spearman correlation between original distance and binary mismatch when (X) is the distance rank, is exactly

[
ho=Delta_{rank}sqrt{p(1-p)}.
]

The same correlation is obtained by the usual sample-covariance convention because the common finite-sample scaling cancels from the correlation coefficient.

## Proof

Because (Y) is binary,

[
E(Y)=p,qquad operatorname{Var}(Y)=p(1-p).
]

The overall mean of (X) is

[
ar X=par X_1+(1-p)ar X_0.
]

Using population-form moments over the finite set of (M) pair observations,

[
egin{aligned}
operatorname{Cov}(X,Y)
&=E(XY)-E(X)E(Y)\\
&=par X_1-par X\\
&=p{ar X_1-[par X_1+(1-p)ar X_0]}\\
&=p(1-p)(ar X_1-ar X_0).
end{aligned}
]

Therefore

[
egin{aligned}
ho
&=rac{operatorname{Cov}(X,Y)}
{sigma_Xsqrt{operatorname{Var}(Y)}}\\
&=rac{p(1-p)(ar X_1-ar X_0)}
{sigma_Xsqrt{p(1-p)}}\\
&=rac{ar X_1-ar X_0}{sigma_X}sqrt{p(1-p)}\\
&=Delta_{rank}sqrt{p(1-p)}.
end{aligned}
]

This proves the identity.

## Consequence 1 — exact state-balance attenuation

For a fixed separation (Delta_{rank}), the ordinary distance–mismatch correlation is multiplied by

[
A(p)=sqrt{p(1-p)}.
]

The multiplier is maximal at (p=1/2), where (A(1/2)=1/2), and approaches zero as mismatch prevalence approaches either 0 or 1. Thus imbalance attenuates the measurable correlation even when the locations of mismatch pairs along the distance-rank axis remain separated.

## Consequence 2 — necessary separation for a declared target

Because

[
sqrt{p(1-p)}le rac12,
]

any positive target (ho^star) requires

[
Delta_{rank}ge 2ho^star.
]

For the frozen target (ho^star=0.15),

[
Delta_{rank}ge0.30
]

is necessary at any state balance. Equality is possible only at (p=0.5).

This does **not** imply that every state configuration with (Delta_{rank}ge0.30) is accessible to a particular stochastic generator. The inequality is a representational requirement; generator accessibility remains a distinct gate.

## Consequence 3 — why balance normalization is diagnostic, not a new preferred estimator

Calibrating (Delta_{rank}) instead of (ho) removes only the exact multiplicative state-balance term. It leaves the same binary states and distance ranks unchanged. The v0.5 comparison therefore asks how much of the original Mk2 calibration loss is attributable to this mathematically identified attenuation component.

It is not proposed as a replacement phylogenetic-signal statistic. The unresolved no-bracket remainder after balance normalization is retained under the pre-frozen stop rule.

## Numerical verification

The committed v0.5 implementation reconstructs both sides of the identity for every analyzed system and reports a maximum absolute factorization error of (8.8818\times10^{-16}), consistent with floating-point rounding.
