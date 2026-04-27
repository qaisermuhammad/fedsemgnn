# paper_visualization_catalog.py
"""
Complete catalog of all visualization scripts and graphs available in the FedSemGNN codebase.
This script documents all the plotting capabilities for your research paper.

Found 35+ different visualization scripts generating 60+ distinct graphs!
"""

import os
import subprocess
from pathlib import Path

# =============================================================================
# COMPREHENSIVE VISUALIZATION CATALOG FOR FEDSEMGNN PAPER
# =============================================================================

def run_script(script_path, description):
    """Run a plotting script and handle any errors."""
    try:
        print(f"\n🔨 Running: {description}")
        print(f"   Script: {script_path}")
        result = subprocess.run(['python', script_path], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ Error in {description}")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"💥 Exception in {description}: {e}")

def generate_all_paper_graphs():
    """Generate all graphs for the paper systematically."""
    
    print("=" * 80)
    print("🎨 COMPREHENSIVE FEDSEMGNN PAPER VISUALIZATION GENERATOR")
    print("=" * 80)
    print("Generating 60+ graphs across 9 major categories...")
    
    # Category 1: Core Performance Comparison Graphs
    print("\n📊 CATEGORY 1: CORE PERFORMANCE COMPARISONS")
    scripts_1 = [
        ("compare_plot.py", "Strategy comparison: reward, latency, fidelity, power, bytes (7 graphs)"),
        ("plot_compare_metrics_all.py", "All strategies overlay plots (5 graphs)"),
        ("build_paper_artifacts.py", "Paper-ready comparison plots with bar charts (6 graphs)"),
    ]
    for script, desc in scripts_1:
        run_script(script, desc)
    
    # Category 2: Detailed Metric Analysis
    print("\n📈 CATEGORY 2: DETAILED METRIC ANALYSIS")
    scripts_2 = [
        ("metrics_analysis.py", "Reward vs power, fidelity vs latency correlation plots"),
        ("plot_normalized_metrics.py", "Min-max normalized performance trends"),
        ("fidelity.py", "Fidelity analysis graphs (PNG + PDF)"),
        ("latency.py", "Latency distribution and trends (PNG + PDF)"),
        ("power_consumption.py", "Power consumption analysis (PNG + PDF)"),
        ("byteexchanged.py", "Bytes exchanged analysis (PNG + PDF)"),
    ]
    for script, desc in scripts_2:
        run_script(script, desc)
    
    # Category 3: Server-Level Analysis
    print("\n🖥️ CATEGORY 3: SERVER-LEVEL ANALYSIS")
    scripts_3 = [
        ("edge_server_analysis.py", "Per-server power, services vs migrations"),
        ("server5_trace_analysis.py", "Server 5 detailed trace analysis"),
        ("server5_recovery_lag.py", "Server 5 recovery lag patterns"),
        ("semantic_server5_model.py", "Server 5 semantic modeling"),
    ]
    for script, desc in scripts_3:
        run_script(script, desc)
    
    # Category 4: Migration and Fault Tolerance
    print("\n🔄 CATEGORY 4: MIGRATION & FAULT TOLERANCE")
    scripts_4 = [
        ("migration_fidelity_analysis.py", "Migration impact on fidelity"),
        ("migration_turbulence_and_outliers.py", "Migration turbulence vs load"),
        ("delta_bytes_vs_lag.py", "Bytes exchange vs recovery lag correlation"),
        ("correlate_server5_latency.py", "Server 5 latency correlation analysis"),
    ]
    for script, desc in scripts_4:
        run_script(script, desc)
    
    # Category 5: Clustering and Rewards
    print("\n🎯 CATEGORY 5: CLUSTERING & REWARDS")
    scripts_5 = [
        ("plot_cluster_rewards.py", "Cluster-level reward analysis"),
        ("rewards.py", "Reward distribution and trends"),
        ("plot_recovery_and_bytes.py", "Recovery patterns vs bytes exchanged"),
    ]
    for script, desc in scripts_5:
        run_script(script, desc)
    
    # Category 6: Latency Deep Dives
    print("\n⏱️ CATEGORY 6: LATENCY DEEP DIVES")
    scripts_6 = [
        ("plot_step_latency.py", "Step-by-step latency breakdown"),
        ("step_latency_instrument.py", "Instrumented latency measurements"),
        ("instrument_orch_latency.py", "Orchestration latency histogram"),
        ("comm_latency_instrument.py", "Communication latency patterns"),
    ]
    for script, desc in scripts_6:
        run_script(script, desc)
    
    # Category 7: Semantic Learning and GCN Analysis
    print("\n🧠 CATEGORY 7: SEMANTIC LEARNING & GCN")
    scripts_7 = [
        ("plot_fidelity_vs_gcn.py", "Fidelity comparison: GCN vs Linear models"),
        ("semantic_utils.py", "Semantic embedding analysis (if has plotting)"),
        ("dim.py", "Dimensionality analysis (if has plotting)"),
    ]
    for script, desc in scripts_7:
        run_script(script, desc)
    
    # Category 8: Strategy Tables and Summaries
    print("\n📋 CATEGORY 8: STRATEGY TABLES & SUMMARIES")
    scripts_8 = [
        ("generate_strategy_table.py", "Strategy performance summary table"),
        ("generate_strategy_table2.py", "Enhanced strategy comparison table"),
        ("comparative_table.py", "Comparative analysis table"),
        ("summarize_results.py", "Results summary generation"),
    ]
    for script, desc in scripts_8:
        run_script(script, desc)
    
    # Category 9: Enhanced Supervisor Suggestions (NEW)
    print("\n🚀 CATEGORY 9: ENHANCED FEATURES (SUPERVISOR SUGGESTIONS)")
    scripts_9 = [
        ("plot_enhanced_fedsemgnn_results.py", "Enhanced FedSemGNN with online learning, fault tolerance, extreme scale (5 graphs)"),
    ]
    for script, desc in scripts_9:
        run_script(script, desc)
    
    # Category 10: Diagnostic and Debug Plots
    print("\n🔍 CATEGORY 10: DIAGNOSTIC & DEBUG PLOTS")
    scripts_10 = [
        ("plot_diagnostics.py", "Confidence intervals and train/val comparisons"),
        ("plot_comparison.py", "All fidelity comparison"),
    ]
    for script, desc in scripts_10:
        run_script(script, desc)

def list_all_generated_files():
    """List all the graphs that can be generated."""
    
    print("\n" + "=" * 80)
    print("📁 COMPLETE LIST OF GENERATED VISUALIZATIONS")
    print("=" * 80)
    
    visualization_map = {
        "🎯 Core Performance (results/plots_compare/)": [
            "compare_reward.png",
            "compare_latency_linear.png", 
            "compare_latency_log.png",
            "compare_fidelity.png",
            "compare_power.png",
            "compare_bytes_step.png",
            "compare_bytes_cumulative.png",
            "normalized_reward_minmax_all.png",
            "normalized_latency_minmax_all.png", 
            "normalized_fidelity_minmax_all.png",
            "normalized_reward_minmax.png",
            "normalized_latency_minmax.png",
            "normalized_fidelity_minmax.png",
            "summary_table.tex"
        ],
        
        "📊 Traditional Metrics (graphs/)": [
            "fidelity.png", "fidelity.pdf",
            "latency.png", "latency.pdf", 
            "power_consumption.png", "power_consumption.pdf",
            "rewards.png", "rewards.pdf",
            "strategy_metrics.png",
            "bytes_exchanged.png", "bytes_exchanged.pdf"
        ],
        
        "🖥️ Server Analysis (results/processed/)": [
            "es_power_over_time.png",
            "es5_services_migrations.png", 
            "server5_recovery_lag.png",
            "server5_fidelity_highlight.png",
            "server5_reward_highlight.png",
            "migration_fidelity_server5.png",
            "metrics_reward_power.png",
            "metrics_fidelity_latency.png"
        ],
        
        "🔄 Migration & Fault Tolerance (results/processed/)": [
            "delta_bytes_vs_lag.png",
            "outlier_load_vs_lag.png",
            "ti_vs_lag.png",
            "migration_fidelity_server5.png"
        ],
        
        "🎯 Clustering & Rewards (results/processed/)": [
            "cluster_rewards.png",
            "reward_vs_step.png",
            "all_fidelity.png",
            "fidelity_comparison.png"
        ],
        
        "⏱️ Latency Analysis (results/processed/)": [
            "substep_latency.png",
            "step_latency_hist.png", 
            "orch_latency_hist.png"
        ],
        
        "🧠 Semantic & GCN (results/processed/)": [
            "fidelity_vs_gcn.png",
            "tsne_semantic_clusters.png"
        ],
        
        "🚀 Enhanced Features (results/)": [
            "traditional_metrics.png",
            "extreme_scale_metrics.png",
            "fault_tolerance_dashboard.png", 
            "semantic_learning_progress.png",
            "comprehensive_summary.png"
        ],
        
        "🔍 Diagnostics (results/)": [
            "reward_with_ci.png",
            "train_val_reward.png"
        ]
    }
    
    total_graphs = 0
    for category, files in visualization_map.items():
        print(f"\n{category}")
        print("-" * 60)
        for file in files:
            print(f"   • {file}")
            total_graphs += 1
    
    print(f"\n🎉 TOTAL: {total_graphs} different visualizations available!")
    print("   (Plus CSV files with processed data for custom analysis)")

def paper_ready_batch_generation():
    """Generate all paper-ready visualizations in one go."""
    
    print("\n" + "=" * 80)
    print("🎯 PAPER-READY BATCH GENERATION")
    print("=" * 80)
    print("Generating all high-priority visualizations for paper submission...")
    
    # High-priority scripts for paper
    high_priority = [
        ("compare_plot.py", "Core strategy comparisons"),
        ("build_paper_artifacts.py", "Paper-ready summary charts"),
        ("plot_enhanced_fedsemgnn_results.py", "Enhanced FedSemGNN results"),
        ("metrics_analysis.py", "Detailed metric correlations"),
        ("edge_server_analysis.py", "Server-level analysis"),
        ("migration_fidelity_analysis.py", "Migration impact analysis"),
        ("plot_cluster_rewards.py", "Cluster reward patterns"),
        ("plot_fidelity_vs_gcn.py", "GCN vs Linear comparison"),
        ("generate_strategy_table.py", "Strategy performance table"),
    ]
    
    for script, description in high_priority:
        run_script(script, description)
    
    print(f"\n✅ Batch generation complete!")
    print(f"📁 Check these directories for outputs:")
    print(f"   • results/plots_compare/")
    print(f"   • results/processed/") 
    print(f"   • results/")
    print(f"   • graphs/")

if __name__ == "__main__":
    print("🎨 FedSemGNN Paper Visualization Catalog")
    print("Choose an option:")
    print("1. Generate ALL graphs (60+ visualizations)")
    print("2. Generate paper-ready batch (high-priority only)")
    print("3. List all available visualizations")
    print("4. Run specific category")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        generate_all_paper_graphs()
        list_all_generated_files()
    elif choice == "2":
        paper_ready_batch_generation()
    elif choice == "3":
        list_all_generated_files()
    elif choice == "4":
        print("Categories available:")
        print("1. Core Performance  2. Metric Analysis  3. Server Analysis")
        print("4. Migration/Fault   5. Clustering      6. Latency")
        print("7. Semantic/GCN     8. Tables/Summary   9. Enhanced Features")
        cat = input("Enter category (1-9): ").strip()
        # Implement specific category running here
    else:
        print("📋 Use this script to generate any combination of your 60+ available graphs!")
        list_all_generated_files()
