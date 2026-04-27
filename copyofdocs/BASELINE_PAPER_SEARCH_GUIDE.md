# Baseline Paper Search Guide for Computer Networks Submission

## Target Journal
**Computer Networks (Elsevier)**
- ISSN: 1389-1286
- Impact Factor: ~5.5
- Focus: Computer networks, distributed systems, edge computing

## Search Strategy

### Phase 1: Find Recent Relevant Papers (2023-2025)

#### Search Query 1: Federated Learning + Edge Computing
```
"Computer Networks" journal "federated learning" "edge computing" (2023 OR 2024 OR 2025)
```

**What to look for:**
- Papers on federated RL for edge orchestration
- Hierarchical federated learning approaches
- Communication-efficient FL methods

**Expected baseline:** Federated PPO/DQN variant

---

#### Search Query 2: Task Placement with RL
```
"Computer Networks" "task placement" OR "service placement" "reinforcement learning" "mobile edge" (2023 OR 2024 OR 2025)
```

**What to look for:**
- Deep RL for task offloading
- Multi-agent RL for edge computing
- DQN, A3C, PPO-based methods

**Expected baseline:** Centralized RL approach

---

#### Search Query 3: GNN for Edge Computing
```
"Computer Networks" "graph neural network" OR "GCN" "edge computing" OR "edge orchestration" (2023 OR 2024 OR 2025)
```

**What to look for:**
- GNN-based resource allocation
- Graph-based service placement
- Topology-aware scheduling

**Expected baseline:** GNN placement without semantics

---

#### Search Query 4: Semantic/Context-Aware Edge
```
"Computer Networks" "semantic" OR "context-aware" "task scheduling" OR "service placement" "edge" (2023 OR 2024 OR 2025)
```

**What to look for:**
- Semantic-aware scheduling
- Context-based task placement
- QoS-aware orchestration

**Expected baseline:** Heuristic semantic method

---

### Phase 2: Filter and Select Papers

#### Selection Criteria:
- ✅ Published in Computer Networks journal (2023-2025)
- ✅ Reports numerical results on comparable metrics
- ✅ Uses simulation-based evaluation
- ✅ Addresses edge computing orchestration
- ✅ Has clear algorithm description

#### Target Metrics to Extract:
1. **Latency** (ms or seconds)
2. **Energy/Power** (W, J, or Joules)
3. **Communication Overhead** (MB, KB, or bytes)
4. **Reward/Utility** (normalized or absolute)
5. **Task Success Rate** (%)
6. **Service Migrations** (count)
7. **Convergence Time** (timesteps or epochs)

---

### Phase 3: Document Findings

For each selected paper, record:

#### Paper Information:
- **Title:**
- **Authors:**
- **Year:**
- **DOI:**
- **Citation Key:** (for BibTeX)

#### Algorithm Details:
- **Method Name:**
- **Approach:** (RL, heuristic, optimization, etc.)
- **Key Features:** (federated, centralized, GNN-based, etc.)

#### Experimental Setup:
- **Simulator Used:**
- **Network Size:** (number of nodes)
- **Simulation Duration:** (timesteps)
- **Workload Type:**

#### Reported Results:
| Metric | Value | Unit | Notes |
|--------|-------|------|-------|
| Latency | | ms | |
| Power | | W | |
| Comm. Overhead | | MB | |
| Reward | | - | |
| Other | | | |

---

## Search Resources

### Option 1: Google Scholar
1. Go to: https://scholar.google.com/
2. Use search queries above
3. Filter by date: 2023-2025
4. Look for "[PDF]" links or "Cite" button

### Option 2: ScienceDirect (if you have access)
1. Go to: https://www.sciencedirect.com/journal/computer-networks
2. Use "Search within this journal" box
3. Apply date filter: 2023-2025
4. Download PDFs through institutional access

### Option 3: IEEE Xplore / ACM Digital Library (backup)
If Computer Networks papers are scarce, also check:
- IEEE Transactions on Mobile Computing
- IEEE/ACM Transactions on Networking
- ACM Transactions on Cyber-Physical Systems

---

## Target: Find 3-5 Papers

### Ideal Baseline Set:
1. **Paper 1:** Federated RL for edge (to compare against your hierarchical FL)
2. **Paper 2:** GNN-based placement (to show benefit of adding semantics)
3. **Paper 3:** Semantic/context-aware method (to show benefit of GNN+RL)
4. **Paper 4:** Standard DRL baseline (DQN/A3C) (to show federated advantage)
5. **Paper 5 (optional):** Recent survey/benchmark paper

---

## Next Steps After Finding Papers

1. Share paper titles and DOIs with me
2. I'll help create:
   - BibTeX entries for references.bib
   - Comparison tables
   - Related work text
   - Discussion of results

---

## Common Issues and Solutions

### Issue: Can't access full papers
**Solution:** 
- Try Sci-Hub (if legal in your country)
- Request from authors via ResearchGate
- Use your university VPN/proxy
- Email authors directly

### Issue: Papers use different metrics
**Solution:**
- Note the differences in comparison table
- Explain in text: "While [X] reports metric Y, we report metric Z which captures similar performance aspect"

### Issue: Different experimental setups
**Solution:**
- Create separate comparison sections
- Clearly state: "Results adapted from [X] under different conditions"
- Focus on relative improvements, not absolute values

---

## Timeline

- **Day 1 (Today):** Search and identify 5-10 candidate papers
- **Day 2:** Read abstracts/results, select 3-5 best matches
- **Day 3:** Extract data, document findings
- **Day 4:** I'll help format for paper
- **Day 5:** Integrate into manuscript

---

## Template for Recording Paper Data

Copy this for each paper you find:

```
PAPER #1
========
Title: 
Authors: 
Year: 
Journal: Computer Networks
DOI: 
Citation Key: 

Algorithm:
- Name: 
- Type: 
- Features: 

Setup:
- Nodes: 
- Duration: 
- Workload: 

Results:
- Latency: 
- Power: 
- Comm: 
- Reward: 
- Notes: 

Comparison Notes:
- Similar to FedSemGNN because: 
- Different from FedSemGNN because: 
```

---

## Contact Me When:
✅ You find candidate papers
✅ You need help understanding a paper
✅ You need data extraction help
✅ You're ready to format comparisons
✅ You have ANY questions

Let's make this work! 🚀
