# 📊 System Diagram Placement Guide for FedSemGNN Paper

## Available Diagrams Analysis

You have **6 high-quality system diagrams** in `diagramsdotandpython/` folder that should be integrated into your paper. Here's where each diagram should be placed:

---

## 🎯 **RECOMMENDED DIAGRAM PLACEMENTS**

### **1. ARCHITECTURE DIAGRAM** 
**File:** `architecture.png` / `architecture.pdf`
**Content:** Full system architecture showing clusters, GCN encoders, PPO agents, federated aggregator
**Placement:** **Section 4: System Architecture (CRITICAL - MUST INCLUDE)**
**Position:** After introducing the three-tier architecture, before diving into components
**Why:** This is your MAIN system diagram showing the complete FedSemGNN architecture with:
- User devices with semantic encoder
- Multiple clusters (Cluster 1, Cluster 2) with edge nodes
- GCN encoders and Local PPO agents per cluster
- Federated Aggregator with DP noise injection
- Global policy distribution
- Intra-cluster sync (K₁) and inter-cluster sync (K₂)

**LaTeX Integration:**
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth]{diagramsdotandpython/architecture.pdf}
\caption{Complete FedSemGNN system architecture showing hierarchical federated learning with semantic embeddings, GNN topology encoding, and two-level synchronization (intra-cluster $K_1=10$, global $K_2=50$).}
\label{fig:system_architecture}
\end{figure}
```

---

### **2. SEMANTIC PIPELINE DIAGRAM**
**File:** `semantic pipeline.png`
**Content:** Detailed semantic encoding pipeline from input to placement decision
**Placement:** **Section 4.2: Semantic Embedding Module**
**Position:** Right after explaining the continual learning encoder
**Why:** Shows the complete semantic processing flow:
- Service/Task Input → Graph/Context Features
- Semantic Encoder → GNN Encoder → Projection Head
- Semantic Vector z → Similarity Search → Placement Decision
- Feedback loop for semantic adaptation

**LaTeX Integration:**
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{diagramsdotandpython/semantic_pipeline.pdf}
\caption{Semantic embedding pipeline showing the flow from service requests through the custom continual learning encoder ($128 \rightarrow 64 \rightarrow 64 \rightarrow 16$), GNN encoding, and similarity-based matching for placement decisions.}
\label{fig:semantic_pipeline}
\end{figure}
```

---

### **3. TOPOLOGY DIAGRAM**
**File:** `topology.png` (needs PDF conversion)
**Content:** Network topology showing 4 clusters with edge nodes and federated aggregator
**Placement:** **Section 5.1: Experimental Setup**
**Position:** After describing the testbed, before baseline algorithms
**Why:** Visualizes the actual network structure used in experiments:
- Cluster 1: XR/AR Tasks
- Cluster 2: Control Systems
- Cluster 3: Video/Text Analytics
- Cluster 4: Overflow/Mixed Tasks
- Federated aggregator with DP sync
- Shows both intra-cluster (K₁) and inter-cluster (K₂) synchronization

**LaTeX Integration:**
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.80\textwidth]{diagramsdotandpython/topology.pdf}
\caption{Experimental network topology consisting of four semantic clusters with 4 edge nodes each, organized by service type. Dashed lines represent intra-cluster synchronization ($K_1=10$), dotted lines show inter-cluster DP synchronization ($K_2=50$).}
\label{fig:network_topology}
\end{figure}
```

---

### **4. WORKFLOW DIAGRAM**
**File:** `workflowdiagram.png`
**Content:** Step-by-step orchestration workflow from service arrival to policy update
**Placement:** **Section 4: System Architecture (after main architecture figure)**
**Position:** After Figure 1 (architecture), showing operational flow
**Why:** Detailed operational workflow showing:
- (0) Service Arrival → (1) Semantic Encoding → (2) GNN Encoding
- (3) Cluster Selection → (4) Placement → (5) Reward Computation
- (6) Local PPO Update → (7) Sync Decision
- (7a) Intra-cluster Sync → (7b) Global DP Aggregation
- (8) Broadcast Updated Policy with feedback loops

**LaTeX Integration:**
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.75\textwidth]{diagramsdotandpython/workflowdiagram.pdf}
\caption{FedSemGNN orchestration workflow showing the complete decision cycle from service arrival through semantic encoding, GNN-based selection, placement execution, reward computation, local PPO update, and hierarchical federated synchronization with global policy broadcast.}
\label{fig:workflow}
\end{figure}
```

---

### **5. MOBILITY DIAGRAM**
**File:** `mobility.png`
**Content:** User mobility and service migration between clusters
**Placement:** **Section 4.4: Hierarchical Federated Coordination OR Section 5: Evaluation**
**Position:** In methodology or when discussing migration stability
**Why:** Illustrates dynamic scenarios:
- Mobile user movement from time t to t+Δt
- Service session handover from Cluster A to Cluster B
- Global policy distribution to both clusters
- Semantic feedback loop for adaptation

**LaTeX Integration:**
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.80\textwidth]{diagramsdotandpython/mobility.pdf}
\caption{Service migration and handover scenario showing user mobility triggering service relocation between Cluster A and Cluster B, with global policy distribution and semantic feedback maintaining QoS consistency.}
\label{fig:mobility_handover}
\end{figure}
```

---

### **6. FAULT TOLERANCE & RECOVERY DIAGRAM**
**File:** `Fault Tolerance & Recovery Loop diagram.png`
**Content:** Health monitoring, failure detection, and recovery loop
**Placement:** ❌ **NOT INTEGRATED - INTENTIONALLY EXCLUDED**
**Reason:** Paper honestly states "our evaluation did not explicitly test fault recovery scenarios" (Limitations section). Including this diagram would contradict the limitation statement and imply functionality that was not implemented or validated.

**Decision:** Maintaining paper integrity by only including diagrams for features that were actually implemented and tested.

---

## 📋 **PRIORITY RANKING**

### **✅ INTEGRATED (Critical for understanding):**
1. ✅ **Architecture Diagram** - Main system overview (Section 4)
2. ✅ **Semantic Pipeline** - Shows your key innovation (Section 4.2)
3. ✅ **Workflow Diagram** - Operational cycle (Section 4.4)
4. ✅ **Topology Diagram** - Experimental setup (Section 5.1)
5. ✅ **Mobility Diagram** - Handover scenarios (Section 5)

### **❌ EXCLUDED (Not implemented/tested):**
6. ❌ **Fault Tolerance Diagram** - Intentionally excluded (contradicts limitation statement)

---

## 🔧 **NEXT STEPS**

### **Step 1: Convert PNG to PDF for LaTeX (Optional Quality Enhancement)**
```bash
# Convert integrated PNG diagrams to PDF format for better LaTeX quality
magick diagramsdotandpython/topology.png diagramsdotandpython/topology.pdf
magick diagramsdotandpython/mobility.png diagramsdotandpython/mobility.pdf
magick diagramsdotandpython/workflowdiagram.png diagramsdotandpython/workflowdiagram.pdf
magick "diagramsdotandpython/semantic pipeline.png" diagramsdotandpython/semantic_pipeline.pdf

# Note: Fault tolerance diagram intentionally NOT converted (excluded from paper)
```

**OR regenerate from DOT files:**
```bash
dot -Tpdf diagramsdotandpython/dotcode/topology.txt -o diagramsdotandpython/topology.pdf
dot -Tpdf diagramsdotandpython/dotcode/mobility.txt -o diagramsdotandpython/mobility.pdf
# etc.
```

### **Step 2: Create figures/ subdirectory**
```bash
mkdir sections/figures
copy diagramsdotandpython\architecture.pdf sections\figures\
copy diagramsdotandpython\semantic_pipeline.pdf sections\figures\
copy diagramsdotandpython\topology.pdf sections\figures\
copy diagramsdotandpython\workflowdiagram.pdf sections\figures\
copy diagramsdotandpython\mobility.pdf sections\figures\
```

### **Step 3: Update LaTeX files**
- Add figure references to `system_architecture_corrected.tex`
- Add topology diagram to `evaluation_corrected.tex` (Experimental Setup)
- Add semantic pipeline to methodology section
- Update all `\ref{fig:...}` citations in text

---

## 📐 **DIAGRAM PLACEMENT MAP**

```
Paper Structure:
│
├── Section 4: System Architecture
│   ├── [FIGURE 1] architecture.pdf ⭐ MAIN SYSTEM DIAGRAM
│   ├── [FIGURE 2] workflowdiagram.pdf ⭐ OPERATIONAL FLOW
│   │
│   ├── 4.2: Semantic Embedding Module
│   │   └── [FIGURE 3] semantic_pipeline.pdf ⭐ SEMANTIC PROCESSING
│   │
│   └── 4.4: Hierarchical Federated Coordination
│       └── [FIGURE 4] mobility.pdf (optional) - HANDOVER SCENARIO
│
├── Section 5: Evaluation and Results
│   ├── 5.1: Experimental Setup
│   │   └── [FIGURE 5] topology.pdf ⭐ NETWORK TOPOLOGY
│   │
│   └── [17 performance graphs already integrated] ✅
│
└── Section 7: Limitations (optional)
    └── [FIGURE 6] fault_tolerance_recovery.pdf (if discussed)
```

---

## ✅ **FINAL RECOMMENDATION**

**Integrate these 3-5 diagrams immediately:**

1. **architecture.pdf** → Section 4 (System Architecture overview)
2. **semantic_pipeline.pdf** → Section 4.2 (Semantic Embedding Module)
3. **topology.pdf** → Section 5.1 (Experimental Setup)
4. **workflowdiagram.pdf** → Section 4 (Operational workflow)
5. **mobility.pdf** → Section 4.4 or 5 (if space allows)

This will give readers a complete visual understanding of:
- ✅ What FedSemGNN is (architecture)
- ✅ How it works (workflow + semantic pipeline)
- ✅ Where it was tested (topology)
- ✅ How it handles dynamics (mobility)
- ✅ What results it achieved (17 graphs already integrated)

**Total figures: 22-23 figures** (5-6 system diagrams + 17 performance graphs)

This is appropriate for a comprehensive conference/journal paper!
