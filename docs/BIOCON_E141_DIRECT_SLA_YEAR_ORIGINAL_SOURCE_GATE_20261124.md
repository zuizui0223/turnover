# BioCON E141: source-only temporal SLA gate (2026-11-24)

## Already confirmed
The original 1997 planting split 12 g m-2 seed equally among the sown species (official Cedar Creek experiment E141). Original author Figshare v3 MD5 verified: 64/64 CO2×N×monoculture species cells have exactly 2 physical plots each; 126/168 original mixed main plots qualify at >=80% 14-of-16 *candidate* directly native SLA coverage, if the two documented neighboring Big Bio substitutes are excluded. These checks do not establish actual measured-trait dates, available annual mono biomass or FD effect.

## Original source fixed before opening any response
Ohlert/Kimmel published original cleaning code uses directly linked publicly hosted EDI knb-lter-cdr.538.9, source path ending d6a22544411064d397041a9548f73074. Cedar Creek original catalog describes package 538 as Photosynthesis (Amax etc.), observed across 1998–2018. The separate original BioCON Specific Leaf Area source in package 322 is listed for 2001. Do not confuse these original source datasets, combine their values or assume raw treated means from all years are pre-sowing traits.

Read only the original file through its public, anonymous official endpoint. Require exact author-code columns CountOfSpecies, measured.species, CO2.Treatment, Nitrogen.Treatment, SLA..cm2.g. and **one unambiguous original calendar year field**. Check SLA value presence only, not numeric SLA value. Restrict to original monocultures, original CO2 and N treatment labels, documented direct source species. Qualifying measurement year for predicting biomass in year t is strictly earlier than t; same-year chronological order is unverified and not eligible. No raw rows, original numeric SLA, biomass, net diversity effect or source species identifiers exported.

If original EDI endpoint returns an access error, no year column, ambiguous year or original source schema differences, STOP with SOURCE_ACCESS_OR_YEAR_HOLD. Do not bypass credentials, take trait values from third parties, impute years or weaken the previously fixed 80% threshold after observing outcomes. A successful source-code CI run may legitimately contain a HOLD scientific result.

Until original source dates are available, the entire E141 FD→NDE/CE/SE/biomass study is NOT an identified causal FD intervention, and remains a single experiment rather than independent multi-site evidence. No prior negative/positive biomass results or Evolution RC4 conclusions are changed.

Source links: https://cedarcreek.umn.edu/research/experiments/e141 ; https://cedarcreek.umn.edu/research/experiments/e141/dataset/photosynthesis-maxetc ; https://github.com/kaitkimmel/FDiv/blob/e61c8814f3fc8e8fa7cac6141ee462c3e8b22554/R/CDRTraitCleaning.R
