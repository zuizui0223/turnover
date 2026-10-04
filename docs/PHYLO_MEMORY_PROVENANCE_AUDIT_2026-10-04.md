# Phylogenetic-memory measurement-frontier provenance audit — 2026-10-04

## Trigger

The v0.3.1 edge-split mechanism workflow was initially written against the categorical population reported in the committed v0.2 result (265 nominal-categorical systems, 251 S3 no-bracket). Direct enumeration of the cited known-truth artifacts returned 276 categorical systems instead.

This discrepancy was investigated before any v0.3.1 mechanism result was opened.

## Authoritative artifact check

### v0.1 measurability

Cited workflow run: 37189463333  
Artifact: 11298294238  
Artifact digest: b56fc553db4ded73ff95720cfbb7b674c0b494e9d6a4d35cff3d783936b0afbd

The artifact scientific quantities match the committed v0.1 result, including:
- 722 systems
- continuous PASS 0.5620767494
- categorical PASS 0.02150537634
- categorical logit coefficient -4.743236395
- +1 SD log-n coefficient 1.755626339

No correction was needed.

### v0.2 calibration decomposition

Cited workflow run: 37191027580  
Artifact: 11298622940  
Artifact digest: bc8cc6dd2e30e47b08c27385d146de1dab2f5d7879ec11f5d822f5e1779f6c16  
SHA-256 of result.json inside the artifact: cd993d3cc0737da3d47b71387cb45cf21e74efec4f439e7ce2c2301eb1b8326d

The artifact contains:
- 683 systems
- 407 continuous / 276 nominal categorical
- continuous no-bracket 60/407 = 14.742%
- categorical no-bracket 220/276 = 79.710%
- categorical adjusted no-bracket OR = 18.416
- continuous calibrated 347; post-calibration failure 54/347 = 15.562%
- categorical calibrated 56; post-calibration failure 38/56 = 67.857%

The previously committed result instead reported 418/265 systems, 83/251 no-bracket, and categorical OR ≈186 while citing this same artifact. Those values therefore were not supported by the cited artifact.

### v0.2.1 breadth audit

Cited workflow run: 37191153634  
Artifact: 11299251201  
Artifact digest: 785ae777ac59b796f0998d707e0de8c054e30afbdb1c97ef83d3dafe1c9f1068  
SHA-256 of result.json inside the artifact: 44f5d224e2097fde2d23be4a47025621867cc69a9f9478c1f1b8fc84ebf348d0

The artifact contains:
- 7 categorical traits
- trait no-bracket range 50.0–86.9%
- median trait no-bracket rate 60.0%
- 3/7 traits >=80%
- 0/7 traits =100%
- 100 families with >=2 categorical systems
- family no-bracket median 100%, IQR 66.7–100%

The previously committed result reported 9 traits, 8/9 >=80%, 4/9 =100%, and 83 families with IQR 100–100%; these were not supported by the cited artifact.

## Scientific impact

The correction changes the strength and shape of the claim, not its sign.

Supported:
- equal benchmark signals are far less recoverable for nominal-categorical than continuous-scalar representations;
- calibration accessibility is a major categorical bottleneck;
- failure is widespread across real family × trait geometries;
- system-specific known-truth recoverability checks are necessary.

Withdrawn or weakened:
- categorical no-bracket is not 94.7%; it is 79.7% in the cited novel-system artifact;
- the adjusted categorical no-bracket OR is 18.4, not 186;
- categorical failure is not nearly uniform across traits;
- CALIBRATION_NO_BRACKET must not be called a hard mathematical ceiling without an attainability test, because 11.4% of categorical no-bracket systems have a maximum frozen-grid median >=0.15.

## Corrective actions

1. Repository v0.2 and v0.2.1 result summaries were replaced with artifact-backed quantities.
2. Their internal artifact result SHA-256 values were added to the committed summaries.
3. The CI contract was rewritten to assert the artifact-backed counts, rates, OR and result hashes.
4. The manuscript skeleton was reframed from a near-universal categorical ceiling to a representation × realized-geometry measurement frontier.
5. v0.3.1 now uses the exact 276-system categorical population and 220 no-bracket systems from the cited v0.2 artifact.
6. The v0.3 unconstrained pair-label upper bound remains superseded before execution; v0.3.1 uses realizable one-edge binary splits.

## Publication rule

No result from the v0.3.1 mechanism analysis should be interpreted until all 276 categorical systems are processed under the corrected population frame and the aggregate artifact is verified against its committed summary.
