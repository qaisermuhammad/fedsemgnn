# Baseline Paper Integration Checklist

Complete this checklist to successfully integrate baseline comparisons into your paper.

---

## Phase 1: Paper Search (Days 1-2)

### Search Execution
- [ ] Run all High Priority queries from GOOGLE_SCHOLAR_QUERIES.md
  - [ ] Query 2A: RL Task Placement
  - [ ] Query 1A: Federated Edge
  - [ ] Query 3A: GNN Edge Computing
  - [ ] Query 4A: Semantic Edge

- [ ] Run Medium Priority queries (if needed)
  - [ ] Query 2C: Task Offloading DRL
  - [ ] Query 1B: Federated RL
  - [ ] Query 4B: Context-Aware

### Initial Screening
- [ ] Found 10-15 candidate papers from Computer Networks
- [ ] Verified publication years (2023-2025)
- [ ] Confirmed papers report numerical results
- [ ] Checked papers use comparable metrics

---

## Phase 2: Paper Selection (Day 2)

### Selection Criteria
- [ ] Selected 3-5 papers that best match FedSemGNN
- [ ] Ensured diversity of approaches:
  - [ ] At least 1 Federated Learning paper
  - [ ] At least 1 GNN-based paper
  - [ ] At least 1 Semantic/Context-aware paper
  - [ ] At least 1 Standard RL baseline

### Paper Access
- [ ] Downloaded PDFs of all selected papers
- [ ] Organized PDFs in folder
- [ ] Can access full text of all papers

---

## Phase 3: Data Extraction (Days 2-3)

### For Each Selected Paper

#### Paper 1: _______________________
- [ ] Filled in PAPER_DATA_COLLECTION.md template
- [ ] Extracted numerical metrics:
  - [ ] Latency value: _______
  - [ ] Power value: _______
  - [ ] Communication overhead: _______
  - [ ] Other metrics: _______
- [ ] Noted experimental setup details
- [ ] Identified table/figure references
- [ ] Documented comparison notes

#### Paper 2: _______________________
- [ ] Filled in PAPER_DATA_COLLECTION.md template
- [ ] Extracted numerical metrics:
  - [ ] Latency value: _______
  - [ ] Power value: _______
  - [ ] Communication overhead: _______
  - [ ] Other metrics: _______
- [ ] Noted experimental setup details
- [ ] Identified table/figure references
- [ ] Documented comparison notes

#### Paper 3: _______________________
- [ ] Filled in PAPER_DATA_COLLECTION.md template
- [ ] Extracted numerical metrics:
  - [ ] Latency value: _______
  - [ ] Power value: _______
  - [ ] Communication overhead: _______
  - [ ] Other metrics: _______
- [ ] Noted experimental setup details
- [ ] Identified table/figure references
- [ ] Documented comparison notes

#### Paper 4: _______________________
- [ ] Filled in PAPER_DATA_COLLECTION.md template
- [ ] Extracted numerical metrics:
  - [ ] Latency value: _______
  - [ ] Power value: _______
  - [ ] Communication overhead: _______
  - [ ] Other metrics: _______
- [ ] Noted experimental setup details
- [ ] Identified table/figure references
- [ ] Documented comparison notes

---

## Phase 4: Citation Management (Day 3)

### BibTeX Entries
- [ ] Found BibTeX for all selected papers
  - [ ] Paper 1 BibTeX added to references.bib
  - [ ] Paper 2 BibTeX added to references.bib
  - [ ] Paper 3 BibTeX added to references.bib
  - [ ] Paper 4 BibTeX added to references.bib

### Citation Keys
- [ ] Used consistent citation key format (e.g., Author2024Method)
- [ ] Verified all required BibTeX fields present
- [ ] Checked DOI links work

---

## Phase 5: LaTeX Integration (Days 4-5)

### Comparison Tables
- [ ] Selected appropriate table template from LATEX_COMPARISON_TEMPLATES.md
- [ ] Filled in all values from collected data
- [ ] Added table to main.tex or evaluation section
- [ ] Verified table compiles without errors
- [ ] Added table caption and label
- [ ] Added table notes explaining differences

### Related Work Section
- [ ] Added subsections for each baseline category:
  - [ ] Federated Learning subsection
  - [ ] GNN-based Methods subsection
  - [ ] Semantic-Aware Methods subsection
  - [ ] Standard RL Methods subsection
- [ ] Cited all selected papers in related work
- [ ] Explained key differences from FedSemGNN
- [ ] Positioned FedSemGNN's contributions

### Evaluation Section
- [ ] Added "Comparison with State-of-the-Art" subsection
- [ ] Wrote comparison text for each baseline paper
- [ ] Explained why FedSemGNN outperforms
- [ ] Noted experimental setup differences
- [ ] Referenced comparison table(s)

### Discussion Section
- [ ] Analyzed relative performance improvements
- [ ] Discussed implications of results
- [ ] Addressed any caveats or limitations
- [ ] Explained significance of improvements

---

## Phase 6: Quality Assurance (Day 5)

### Data Verification
- [ ] Double-checked all extracted numerical values
- [ ] Verified values match source papers
- [ ] Confirmed units are consistent (ms, W, MB, etc.)
- [ ] Checked calculations for improvement percentages

### Citation Verification
- [ ] All citations compile correctly
- [ ] Citation keys match references.bib
- [ ] All cited papers appear in reference list
- [ ] Reference format follows journal style

### Table Quality
- [ ] Tables are well-formatted
- [ ] Column alignment is correct
- [ ] Bold formatting highlights FedSemGNN
- [ ] Table notes are clear and complete
- [ ] Tables fit within page margins

### Text Quality
- [ ] Comparison text is clear and objective
- [ ] No overclaiming or unfair comparison
- [ ] Differences in setup are acknowledged
- [ ] Writing flows well and is concise

---

## Phase 7: Final Review (Day 5-6)

### Completeness Check
- [ ] All selected papers are cited
- [ ] All comparison tables are complete
- [ ] All sections reference the tables
- [ ] No placeholder text remains (e.g., [X], [value])

### Consistency Check
- [ ] Terminology is consistent throughout
- [ ] Metric names match across text and tables
- [ ] Citation format is consistent
- [ ] Numbers match between text and tables

### Compilation Check
- [ ] LaTeX compiles without errors
- [ ] All tables render correctly
- [ ] All citations resolve
- [ ] PDF looks professional

---

## Quick Reference Numbers

Your FedSemGNN baseline results to compare against:

| Metric | Value |
|--------|-------|
| Normalized Reward | 0.91 |
| Latency | 0.36 ms |
| Power | 72.1 W |
| Communication | 0.65 MB |
| Semantic Fidelity | 100% |
| Migrations | 0 |
| Comm. Efficiency | 1.394 reward/MB |

Your implemented baselines:

| Baseline | Latency | Power | Comm. | Reward |
|----------|---------|-------|-------|--------|
| FlatFedPPO | 114.25 ms | 2607.9 W | 105.0 MB | 0.84 |
| HierFedPPO | 80.71 ms | 1057.4 W | 32.5 MB | 0.78 |
| HSQF | 45.82 ms | 534.7 W | 16.4 MB | 0.69 |
| Random | 112.50 ms | -- | -- | 0.31 |

---

## Timeline Summary

- **Day 1:** Search for papers (4-6 hours)
- **Day 2:** Select and download papers (2-3 hours)
- **Day 3:** Extract data and create BibTeX (4-5 hours)
- **Day 4:** Create tables and update related work (3-4 hours)
- **Day 5:** Write comparison text and discussion (3-4 hours)
- **Day 6:** Final review and polish (2-3 hours)

**Total estimated time: 18-25 hours over 6 days**

---

## Help Points

Contact me (share progress) when you:
- ✅ Complete paper search (show candidate list)
- ✅ Select final papers (confirm choices)
- ✅ Finish data extraction (share filled template)
- ✅ Ready to create tables (I'll help format)
- ✅ Need help with comparison text
- ✅ Ready for final review

---

## Success Criteria

You'll know you're done when:
- ✅ You have 3-5 literature baselines from Computer Networks
- ✅ All baselines are cited and compared
- ✅ Comparison tables are complete and polished
- ✅ Related work properly positions FedSemGNN
- ✅ Evaluation shows clear improvements
- ✅ Paper compiles and looks professional

---

## Notes and Observations

Use this space to track progress and issues:

**Papers found:**


**Challenges encountered:**


**Questions for helper:**


**Additional ideas:**


---

**Remember:** Quality over quantity. 3-4 well-chosen and thoroughly compared baselines 
are better than 10 poorly integrated ones!

Good luck! 🚀
