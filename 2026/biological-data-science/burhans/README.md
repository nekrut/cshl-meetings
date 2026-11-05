# HighGen — CSHL Biological Data Science 2026 Poster

**Title:** HighGen—Comparative genomics resources for cannabis  
**Authors:** Richard C. Burhans, Anton Nekrutenko (Penn State University)  
**Conference:** CSHL Biological Data Science (November 4–7, 2026)  
**Dimensions:** 44 × 44 in (`@page { size: 44in 44in; margin: 0; }`, fits 4 × 4 ft CSHL poster boards)

## Files

- `template.html` — 44 × 44 in HTML/CSS poster source (follows `writing` repository style rules: zero semicolons in prose or SVG labels, closed em-dashes, Okabe-Ito colorblind-safe figures).
- `generate_poster_figures.py` — Generates the five data-dense SVG figures directly from primary TSV/BED files in `cannabis-genome`:
  - `figures/figure1_architecture.svg` — Depositor soft-masking as arrived (`0.0–80.9%` across 218 assemblies) vs. the 4-detector union on the five calibration genomes (`62.9–67.0%`), with a line at the 63% of `cs10` that Grassa et al. (2021) masked, paired with the 185-cut `cs10` gap-boundary reference split map (`wfi_cs10_splits.bed`, 195 chromosomal ~5 Mb pieces, 0 genes cut).
  - `figures/kmer_bands_k21.svg` — Empirical Meryl $k = 21$ multiplicity-weighted occurrence spectra across 12 representative assemblies (`cs10`, 8 Pike et al. 2026 ONT haplotypes, 2 IMPD T2T haplotypes, and diploid `Cannbio-2`).
  - `figures/figure2_matrix_calibration.svg` — `EH23a × EH23b` identity spectrum before and after single-chain colinearity (`331.05M` pooled `[85, 95)%` pairs), pre-registered held-out map on the first 20 Mb of all ten chromosomes (`Cb2 × cs10`, `10/10` at 20 Mb and `67/70` 1 Mb windows won vs HOXD70), and symmetric `4×4` log-odds matrix (`+80/+100` matches, `682/51` gap scaling).
  - `figures/figure3_scalability_benchmarks.svg` — 216-query syntenic (`synNet`, median `65.2%`) and reciprocal-best (`rbest`, median `70.0%`) coverage waterfall across `cs10` (`query_coverage.tsv`), chunked `≤50k`-segment LASTZ speedup (`7.8×`, 1.79 h for the 100 jobs) and `-56.5%` collection purge summed over runs, and MULTIZ benchmarks (`51.7×` RAM reduction from 11.3 streaming, `33.8×` on one deep merge and `4.9×` on one 4.4 Mb piece from 11.4 column-count DP, medians of three same-host runs).
  - `figures/chr7_25.022-31.033Mb_cbs_overview.png` & `figures/multiz_cbdas.png` — Live HighGen 228-stanza (219-assembly) UCSC Genome Browser Track Hub screenshots across the 6 Mb `cs10` chromosome 7 cannabinoid synthase super-cluster (`CBCAS` and `CBDAS` cassettes) and the `multiz217way` alignment track at functional `CBDAS` (`LOC115697762`).
  - `figures/figure4_tandem_clusters.svg` — 216-query `CBDAS` stratification (`79` at `≥98.5%`, `77` at `93.0–98.5%` of which `63` are annotated on the B-locus pseudogene, `6` aligned `<93.0%`, `54` `<50%` CDS pruned in `synNet`) and `netFilter -syn` pruning beside the `46.4%` of recovered pairs (569/1,225) that overlap another family gene.
  - `figures/figure5_panagram_kmer.svg` — Chromosome-wide `AH3Mb.chrY` (`0–110.7 Mb`) Panagram $k = 21$ pseudoautosomal (`0–29.08 Mb`) vs. male-specific Y (`205,619` Y-mers, males `0.976–0.987` vs. V3 females `≤0.077`) profile, 1 Mb window `rbest` chain correlation scatter on `GRMa` (`631` windows, `r = 0.8118`), and Tier P2 (`41/42` passing), TOGA2 v2.0.9 pilot (control plus three EH23a arms, none chosen), and 1,341-record phenotype ledger scorecards.
- `build.py` — Renders `template.html` to `cannabis-poster.pdf` (44 × 44 in) and `poster-preview.png` via headless Chromium (`uv run --with playwright python build.py`).
- `cannabis-poster.pdf` & `poster-preview.png` — Rendered 44 × 44 in print PDF and thumbnail preview.
- `galaxy-logo.svg`, `qr-hub.svg`, `qr-tools.svg`, `qr-repo.svg` — Vector logo and QR codes.

![HighGen Poster Preview](poster-preview.png)
