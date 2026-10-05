# Exact factorization of binary Spearman phylogenetic-memory signal

## Setup

Consider the M unordered tip pairs of one realized phylogeny.

Let:

- X be the average-tie rank of pairwise patristic distance;
- Y be binary pairwise mismatch, with Y=1 when the two tips have different states and Y=0 otherwise;
- p = mean(Y), the fraction of unordered pairs that mismatch;
- mu_1 = mean(X | Y=1);
- mu_0 = mean(X | Y=0);
- sigma_X = population standard deviation of X over all M pairs.

For a binary trait with both states represented, 0 < p < 1.

## Proposition

The Spearman correlation between patristic distance and binary mismatch is exactly

`rho = Delta_rank * sqrt(p(1-p))`

where

`Delta_rank = (mu_1 - mu_0) / sigma_X`.

## Proof

Spearman correlation is Pearson correlation after replacing each variable by its average-tie ranks.

The ranked patristic distance is X by definition.

Because Y is binary, its average-tie rank takes exactly two values. Therefore rank(Y) is an affine transformation of Y with positive slope. Pearson correlation is unchanged by positive affine transformation, so

`Spearman(distance, mismatch) = Corr(X,Y)`.

For binary Y,

`E[Y] = p`

and

`Var(Y) = p(1-p)`.

Also,

`E[XY] = p * mu_1`.

The unconditional mean of X is

`mu_X = p*mu_1 + (1-p)*mu_0`.

Hence

`Cov(X,Y) = E[XY] - E[X]E[Y]`

`= p*mu_1 - p*(p*mu_1 + (1-p)*mu_0)`

`= p(1-p)(mu_1-mu_0)`.

Therefore

`Corr(X,Y) = Cov(X,Y)/(sigma_X*sqrt(p(1-p)))`

`= ((mu_1-mu_0)/sigma_X) * sqrt(p(1-p))`

`= Delta_rank * sqrt(p(1-p))`.

QED.

## Consequence for the rho = 0.15 benchmark

For every p in (0,1),

`sqrt(p(1-p)) <= 0.5`,

with equality at p=0.5.

Therefore

`|rho| <= 0.5 * |Delta_rank|`.

A positive target rho = 0.15 can only be attained if

`Delta_rank >= 0.15 / 0.5 = 0.30`.

Thus **Delta_rank = 0.30 is the minimum unattenuated rank separation capable of supporting rho = 0.15 under any binary state balance**.

This makes the v0.5 diagnostic directional:

- if a system cannot reach Delta_rank = 0.30, no adjustment of binary state balance alone can make rho reach 0.15;
- if a system reaches Delta_rank = 0.30 while the original rho route does not reach 0.15, state-balance attenuation is sufficient to explain at least that accessibility loss.

## Finite-n note

For a finite number of tips, the realizable mismatch-pair prevalence p is discrete and need not equal exactly 0.5. The inequality above remains exact because sqrt(p(1-p)) never exceeds 0.5.

Therefore using 0.30 is conservative with respect to realizable finite-n state balances: it is a necessary threshold, not an assumption that every tree can realize p=0.5 exactly.

## Numerical verification

The v0.5 implementation calculates both:

1. Delta_rank directly from the mean distance-rank separation between mismatch and match pairs; and
2. rho / sqrt(p(1-p)).

The workflow fails if their absolute difference exceeds 1e-10 in any finite replicate. This makes the factorization an executable identity check rather than a prose-only argument.
