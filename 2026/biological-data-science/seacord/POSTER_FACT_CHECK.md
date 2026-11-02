# Poster fact-check: v2

Content review against `disassembler` and `disassembler-dump`, 2026-11-02.
Every item cites the file that settles it, so each box can be closed by reading
one source rather than re-deriving the number.

The headline risk is timing: several of the poster's SARS-CoV-2 and *H. pylori*
numbers come from disassembler 0.1.0, and the 0.1.1 reruns committed on
2026-11-01 and 2026-11-02 change them. One of them is reversed outright.

## Status

Applied to `v2/poster.html` on 2026-11-02: sections 1, 2.2 through 2.5, and
all of 3. Two items are deferred and need a decision, both marked **DEFERRED**
below: 2.1 (which walker20k run to cite) and 2.6 (sieve count).

`v2/poster.pdf` has **not** been regenerated. Every asset the HTML references
(`figures/`, the logos, the QR SVGs, `../chilton/assets/galaxy_logo_white.svg`)
is missing from `v2/`, so a rebuild would render with broken images. The PDF
still shows the pre-fix text.

---

## 1. Blocking: claims the repo's own later work contradicts

### 1.1 "only LexicMap-permissive catches 1.15 M Alpha/Delta-era runs strict loses"

- [x] **Applied.** Panel C finding now reads "Permissive tiering calls 1.15 M
      runs clean full-length against strict's 0.91 M".

`sars-cov-2/lexicmap/disassembler-0.1.1/README.md` carries a section titled
"The 0.1.0 strict-versus-permissive conclusion does not hold". The 0.1.0 result
was an artifact: every deletion counted as an untiled stretch, so no carrier of
a spike deletion could be full length.

| clean full-length | 0.1.0 | 0.1.1 |
|---|---:|---:|
| strict | 76,360 | 910,851 |
| permissive | 1,154,590 | 1,153,371 |
| what strict misses | 1,078,230 | **242,520** |

Strict now holds 79% of permissive's clean full-length cohort, and what it
lacks is rare: none of the 977 permissive-only amino acid variants has more
than 67 carrier accessions, and 958 have 10 or fewer.

Two separate errors were fixed, not one. Even on 0.1.0 numbers, 1.15 M was
permissive's *total*, which includes everything strict also caught; the runs
strict lost were 1.08 M.

The replacement quotes both tier counts directly rather than their difference,
which avoids assuming strict is a subset of permissive under 0.1.1. That
subset relation is stated for 0.1.0 and for the variant catalog, but not for
0.1.1 accessions.

### 1.2 "4.99 M subject genomes in the LexicMap index, the universe each query scans"

- [x] **Applied.** Tile is now "Logan runs hit / 4.99 M / distinct Logan runs
      returning at least one spike HSP."

4,987,809 is the count of distinct subjects that returned at least one HSP for
this one spike query. It is a result of the query, not a property of the index.

- `sars-cov-2/lexicmap/README.disassembler-0.1.0.md`: "Unique subject genomes
  (SRA/ENA/DDBJ runs): 4,987,809"
- same file: the index itself is not recoverable from the output. "The
  underlying subject index is almost certainly Logan", and "if the Galaxy run
  concatenated multiple Logan sub-indices, that information is lost here."
- the kmindex route scanned a different universe, 5,198,305 scored accessions
  (`comparison.disassembler-0.1.0.md`), so "the universe each query scans" is
  not a single number across the two routes.

### 1.3 "Only the walker touches the divergent tail"

- [x] **Applied.** The negative is now stated once, in panel C: "only the
      walker samples the divergent tail, where reconstruction still fails."
      The Route A side box bullet "Divergent tails a single-reference search
      never reaches" was replaced with "Multi-anchor search. Eleven strain
      anchors on spike, not one reference."

The walker samples the divergent tail and recovers nothing from it. In the
`[0.30, 0.70)` score bin: 0 successes out of 200, in both versions.

- `sars-cov-2/kmindex/disassembler-0.1.1/README.md`: "**The divergent tail is
  still empty.**" By score bin, successes are 691 then 690 of 1,000, 30 then 29
  of 300, and none of 200.
- `sars-cov-2/comparison.disassembler-0.1.0.md` calls it "the practical ceiling
  of the current method on this host".

The side box is titled "When the walker route wins", so the honest negative
does not belong there. Multi-anchor is a real win and is documented in
`disassembler/docs/walker.md` (multi-anchor mode) and in the comparison doc,
which attributes divergent-tail reach to "bin stratification + 11-strain
anchoring".

---

## 2. Numbers superseded by the 0.1.1 reruns

### 2.1 WALKER20K OK: 9,448 (47.2%)

- [ ] **DEFERRED, needs a decision.** Left at 9,448.

`sars-cov-2/metadata/results/walker20k/disassembler-0.1.1-corrected-panel/README.md`
says of itself "**This is the run to use**". The cited run used a spike panel
with three defective records: `Delta_B16172` frameshifted from codon 95 by a
deleted IUPAC `Y`, and `Omicron_BA2` / `Omicron_XBB15` carrying 268 and 477 Ns.
Successes go 9,448 to 9,405 (54 lost, 11 gained).

**Why it was not applied.** The contamination analysis in panel E exists only
for the 9,448 run. The corrected-panel README states under "Not regenerated"
that "the bucket tables and figures in `../`" are unchanged, and
`bucket_summary_corrected.tsv` is keyed to the 9,448 wave. Changing panel C to
9,405 while panel E's four percentages, its "1 in ~9,500", its "0 / 6,827" and
the bars in `metadata_bars_poster.png` all rest on 9,448 would desync the
poster against itself for a 0.45% difference.

Three ways to close it:

1. Keep 9,448 and add a version note somewhere in panel C. Cheapest, and the
   contamination conclusion is robust across every tier definition anyway.
2. Rerun the bucket classifier on the corrected-panel cohort, then move the
   whole poster to 9,405 and regenerate `metadata_bars_poster.png`.
3. Leave it. The panel defect changed anchor choice and ORF quality, not the
   success count materially or the contamination result at all.

### 2.2 CLEAN_FULL: 6,827

- [x] **Applied as a disclosure, not a replacement.** The tier rule is now
      printed in the tile: "cov >= 1, pid >= 95". The count stays 6,827 so
      panel C and panel E agree, and so the tile matches the bars in the
      metadata figure.

`sars-cov-2/metadata/results/walker20k/disassembler-0.1.1/README.md` has a
section headed "The CLEAN_FULL tier needs a new definition". The rule was
coverage >= 1.0 against the chosen anchor, and 0.1.0's anchor ranking picked
the shortest records (XBB.1.5 and JN.1 for 7,838 of 9,448 primaries), which
made that easy to clear. The same rule on 0.1.1 primaries keeps **2,780**.

Candidate replacements the repo already evaluated, with the contamination
result attached to each. Any of these is a clean swap only if the metadata
figure is regenerated with it:

| tier | n | C mislabeled | 95% upper bound |
|---|---:|---:|---:|
| success | 9,448 | 1 | 0.059% |
| CLEAN_FULL, 0.1.0 primaries | 6,827 | 0 | 0.054% |
| CLEAN_FULL rule, 0.1.1 primaries | 2,780 | 0 | 0.133% |
| 0.1.1, cov >= 0.99 and pident >= 95 | 8,571 | 0 | 0.043% |
| 0.1.1, complete ORF and pident >= 95 | 6,329 | 0 | 0.058% |

### 2.3 pid 98.75

- [x] **Applied.** Removed. The tile now carries the tier rule instead.

`sars-cov-2/metadata/results/walker20k/walker_quality_summary.tsv` gives
`pident_mean 98.75` over all **9,448 successes**, not over the 6,827
CLEAN_FULL subset the tile paired it with. The corrected-panel 0.1.1 median is
99.85, so the number was both misattributed and stale.

### 2.4 oipA strict panel: 1,042 clean accessions

- [x] **Applied as a label.** Legend now reads "1,042 clean accessions under
      0.1.0 tiering". The count was kept because the heatmap itself is drawn
      from the 0.1.0 `oipa.clean.accessions.fasta`, so changing the number
      alone would contradict the rows on display.

`h-pylori/disassembler-0.1.1/README.md`: `oipa_strict` tier 1 goes 1,042 to
864, 39 distinct rows lost and 1 gained. The cause is real biology worth
knowing at the poster: the 5' CT-repeat phase-variation insertions
(`35_36insTC`, `insTCTC`) are frameshifts under 0.1.1. The README notes "a
selection analysis that wants them has to take them from the flagged tier".

Regenerating the figure from the 0.1.1 baseline would let the legend say 864.

### 2.5 "Four audit tiers per marker"

- [x] **Applied.** Finding and tile now say five.

0.1.1 adds `FLAGGED_FRAMESHIFT`, giving clean full-length, clean partial,
flagged frameshift, flagged premature stops, low-coverage fragment.

This is deliberately a statement about the released tool rather than about the
displayed cohort, which is why the oipA legend is separately marked as 0.1.0
tiering. On 0.1.0 the old claim was exactly right and "every accession
accounted for" checks out against
`h-pylori/baseline/oipa_strict/oipa.summary.json`: 1,042 + 801 + 4 + 1,237 =
3,084 = `total_accessions_evaluated`.

### 2.6 PERM. SIEVED: 79,621

- [ ] **DEFERRED.** Left at 79,621, which matches the figure.

0.1.1 gives 79,354 at the same gap limit, or 123,294 at 0.1.1's new default
limit of 0.25. The lower panel of `spike_poster.png` is drawn from the 0.1.0
`sieved_permissive` MSA (79,620 rows plus the reference), so the printed count
and the rows on display currently agree. Changing one means regenerating the
other.

---

## 3. Overstatements of degree

### 3.1 "the walker drives contamination to zero" and "0.555% to 0%"

- [x] **Applied.** The interval now appears twice: in the contamination-filter
      tile ("0 of 6,827; 95% CI <= 0.054%") and in the panel E cell
      ("0 / 6,827; 95% CI <= 0.054%"). The section heading was left as is,
      since a zero point estimate is a fair summary with the interval printed
      directly beneath it.

The point estimate is correct: 0 of 6,827, confirmed in
`results/walker20k/bucket_summary_corrected.tsv`. But it is zero *observed*,
and the repo never drops the bound. `sars-cov-2/README.md` and the comparison
doc both carry the 95% Clopper-Pearson upper bound of 0.054%, and the repo's
own phrasing is "down to **effectively** 0%".

The interval makes this more defensible, not less, and it survived every
alternative tier definition in section 2.2.

### 3.2 "Hands off to the walker below 85% median identity"

- [x] **Applied.** Now "Divergence check. Flags queries below 85% median
      identity for the walker."

`disassembler/docs/lexicmap.md`: if median identity is below 85% or median
coverage below 0.60, the target is called divergent and "the log **recommends**
the walker route instead". Nothing is routed automatically, so "handoff"
claimed orchestration the tool does not do.

### 3.3 "per-site allele frequencies"

- [x] **Applied.** Now "per-site allele-frequency proxies".

`disassembler/docs/vcf_example.md`, caveats section: "Frequencies are `ka:f`
coverage ratios at a graph fork, a proxy for allele frequency, **not read
counts**, and they can be distorted where a unitig is repeat-collapsed." Also
per-site and unphased, and substitutions only, with indel alleles staying in
`alt_haplotypes.fasta`.

### 3.4 "27 diversifying sites"

- [x] **Applied.** Now "27 diversifying sites (MEME, *p* <= 0.05)".

From `showcase/README.md` Table 1A, these are MEME sites at p <= 0.05,
uncorrected. The same table reports q-values for the *H. pylori* genes (oipA:
"32, 4 at q <= 0.10"), so an informed reader will ask what happens to 27 under
correction. 110 of the 1,274 spike codons are variable.

E484K itself is robust and does not need hedging: LRT 16.32, p = 1.21e-4,
which clears Bonferroni across the 110 variable codons.

### 3.5 "161 global spike haplotypes"

- [x] **Applied.** Legend now reads "160 global spike haplotypes plus the
      Wuhan reference". The stat cell still shows 161, which is consistent.

`showcase/scripts/01_prepare_inputs.py` builds the cohort as `Wuhan_Hu1_ref`
plus the top 160. The ">500k SRA runs" figure is exact and verified:
`showcase/data/prep_manifest.json` has
`"global_sra_runs_represented": 545898`, summed over the 160 haplotypes with
the reference row excluded. That is 47% of the 1.15 M permissive clean
full-length cohort.

### 3.6 "METATRANSCRIPTOMIC_BCT dominates: obelisks live in bacterial microbiome transcriptomes"

- [x] **Applied.** Now framed as corroboration: "dominates the hit
      distribution, matching the published finding that obelisks live in
      bacterial microbiome transcriptomes."

`obelisk/README.md`: the evidence is qualitative, "biggest hit JSONs, up to
11 KB", and the conclusion is attributed, "matching Zheludev et al.'s finding
that obelisks live in bacterial microbiome transcriptomes". There is no
per-index hit table to show if someone asks for the quantitative version.

### 3.7 "a 55/45 HSP pair that fails qcovHSP >= 80"

- [x] **Applied.** Now "stitches HSP pairs that fail `qcovHSP >= 80` alone".

The 55/45 split is an illustrative example in `disassembler/docs/lexicmap.md`,
not a measured case, but it read on the poster like a specific observation.

---

## 4. Verified correct, no action

- [x] 5.88 M HSPs. `stats/basic_stats.txt` via
      `README.disassembler-0.1.0.md`: 5,878,944.
- [x] 24 GB streamed. The file is 25.5 GB, so this is the GiB figure. Harmless,
      but inconsistent with the 0.1.1 README's "25.5 GB" if both are quoted.
- [x] Metadata percentages, all exact against
      `results/walker20k/bucket_summary_corrected.tsv` and
      `results/per_cohort_summary.tsv`: walker20k input 0.555%, success 0.011%
      (1 of 9,448, so "1 in ~9,500" holds), CLEAN_FULL 0.000%, LexicMap
      permissive 0.084%.
- [x] Six cohorts, 2026-09-11 ENA snapshot, zoomed 90-100%. The zoom is
      `ax.set_xlim(0.90, 1.0)` in `scripts/plot_metadata_bars_poster.py`.
- [x] Obelisk tiles: 924 unique runs, 0.97 max containment (alpha), 141 shards
      (28 + 62 + 22 + 29), 5 centroids. All from `obelisk/README.md`.
- [x] Obelisk figure: Oblin-1 (50, 659) and Oblin-2 (695, 875, +) match
      `obelisk/scripts/plot_obelisk_msa_heatmap.py` exactly, and alpha is one
      of only two obelisks carrying "a bona fide tandem Oblin-2 downstream of
      Oblin-1 on the same strand".
- [x] Zika NS5, ~50 contig fragments, one clean walk.
      `docs/contigs_vs_unitigs.md`: ~50 to 63 fragments, no single contig
      holding more than 8% of the gene, walker recovering the full 2,708 nt in
      all nine accessions.
- [x] "memory is O(haplotypes), not O(rows)". Verbatim from
      `docs/lexicmap.md`.
- [x] *H. pylori* 25-gene panel: 20 strict plus 5 loose, and oipA is the only
      finished HyphAeon pass. `h-pylori/README.md`.
- [x] HyphAeon panel: E484K LRT 16.32, total runtime 29.52 s, no input tree.
      `showcase/README.md` Table 1A.
- [x] Spike figure panel order: top is kmindex to walker 20k, bottom is
      LexicMap permissive, shared 3,822 nt frame, RBD span 954-1623. Matches
      `scripts/plot_spike_msa_poster.py`.
- [x] Zenodo DOI `10.5281/zenodo.23737199` and `github.com/nekrut/disassembler`.
- [x] CSHL Biological Data Science 2026, November 4-7. Confirmed against the
      CSHL meetings site, not the repo.

---

## 5. Not checkable from either repo

- [ ] The six NIH and two NSF grant numbers in the acknowledgements.
- [ ] The three related CSHL posters named in the footer.

---

## What is left

1. Decide 2.1, the walker20k run. It is the only open content question.
2. Restore the `v2/` assets and rebuild `v2/poster.pdf`, which still carries
   the pre-fix text.
3. Optional, and only worth it together: regenerate the oipA and spike figures
   from the 0.1.1 baselines, which would let 2.4 and 2.6 print current numbers
   instead of labelled 0.1.0 ones.
