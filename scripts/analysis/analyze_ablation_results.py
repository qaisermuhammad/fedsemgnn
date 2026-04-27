import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

RESULTS_DIR = 'ablation_results'

# List all ablation result folders
def get_ablation_folders():
    return [f for f in os.listdir(RESULTS_DIR) if os.path.isdir(os.path.join(RESULTS_DIR, f))]

def collect_metrics():
    ablations = get_ablation_folders()
    summary = []
    # Collect ablation results
    for ablation in ablations:
        folder = os.path.join(RESULTS_DIR, ablation)
        metrics_files = glob.glob(os.path.join(folder, '*_metrics.csv'))
        for mf in metrics_files:
            algo = os.path.basename(mf).replace('_metrics.csv', '')
            try:
                df = pd.read_csv(mf)
                final_reward = df['Reward'].iloc[-1] if 'Reward' in df.columns else None
                avg_latency = df['Latency_ms'].mean() if 'Latency_ms' in df.columns else None
                avg_fidelity = df['Fidelity_pct'].mean() if 'Fidelity_pct' in df.columns else None
                avg_power = df['Power_W'].mean() if 'Power_W' in df.columns else None
                total_migrations = df['Migrations'].sum() if 'Migrations' in df.columns else None
                total_bytes = df['Bytes_cum_MB'].iloc[-1] if 'Bytes_cum_MB' in df.columns else None
                summary.append({
                    'ablation': ablation,
                    'algorithm': algo,
                    'final_reward': final_reward,
                    'avg_latency': avg_latency,
                    'avg_fidelity': avg_fidelity,
                    'avg_power': avg_power,
                    'total_migrations': total_migrations,
                    'total_bytes': total_bytes
                })
            except Exception as e:
                print(f'Error reading {mf}: {e}')
    # Collect non-ablated (complete system) results
    results_dir = 'results'
    metrics_files = glob.glob(os.path.join(results_dir, '*_metrics.csv'))
    for mf in metrics_files:
        algo = os.path.basename(mf).replace('_metrics.csv', '')
        try:
            df = pd.read_csv(mf)
            final_reward = df['Reward'].iloc[-1] if 'Reward' in df.columns else None
            avg_latency = df['Latency_ms'].mean() if 'Latency_ms' in df.columns else None
            avg_fidelity = df['Fidelity_pct'].mean() if 'Fidelity_pct' in df.columns else None
            avg_power = df['Power_W'].mean() if 'Power_W' in df.columns else None
            total_migrations = df['Migrations'].sum() if 'Migrations' in df.columns else None
            total_bytes = df['Bytes_cum_MB'].iloc[-1] if 'Bytes_cum_MB' in df.columns else None
            summary.append({
                'ablation': 'complete_system',
                'algorithm': algo,
                'final_reward': final_reward,
                'avg_latency': avg_latency,
                'avg_fidelity': avg_fidelity,
                'avg_power': avg_power,
                'total_migrations': total_migrations,
                'total_bytes': total_bytes
            })
        except Exception as e:
            print(f'Error reading {mf}: {e}')
    return pd.DataFrame(summary)

def plot_summary(summary_df):
    # Sort ablation columns for consistent plotting
    ablation_order = sorted(summary_df['ablation'].unique(), key=lambda x: (x != 'complete_system', x))
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 12
    
    # 1. Bar plot: Final Reward
    plt.figure(figsize=(12, 7))
    pivot_reward = summary_df.pivot(index='algorithm', columns='ablation', values='final_reward')[ablation_order]
    ax = pivot_reward.plot(kind='bar', rot=0, width=0.8, edgecolor='black', capsize=4)
    plt.title('Final Reward by Algorithm and Ablation', fontsize=16, fontweight='bold')
    plt.ylabel('Final Reward', fontsize=14)
    plt.xlabel('Algorithm', fontsize=14)
    plt.legend(title='Ablation', fontsize=11, title_fontsize=12, loc='best')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(RESULTS_DIR, 'final_reward_comparison.png'), dpi=500, facecolor='white')
    plt.close()
    print("Created: ablation_results/final_reward_comparison.png")

    # 2. Bar plot: Average Latency (Log Scale)
    plt.figure(figsize=(12, 7))
    pivot_latency = summary_df.pivot(index='algorithm', columns='ablation', values='avg_latency')[ablation_order]
    ax = pivot_latency.plot(kind='bar', rot=0, width=0.8, edgecolor='black', capsize=4, legend=True)
    plt.yscale('log')
    plt.title('Average Latency by Algorithm and Ablation (Log Scale)', fontsize=16, fontweight='bold')
    plt.ylabel('Average Latency (ms, log scale)', fontsize=14)
    plt.xlabel('Algorithm', fontsize=14)
    plt.legend(title='Ablation', fontsize=11, title_fontsize=12, loc='best')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7, which='both')
    
    # Highlight fedsemgnn bars with bold edge and add value labels
    for container, ablation in zip(ax.containers, ablation_order):
        for i, bar in enumerate(container):
            if pivot_latency.index[i] == 'fedsemgnn':
                bar.set_edgecolor('black')
                bar.set_linewidth(3)
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, rotation=90)
    
    plt.savefig(os.path.join(RESULTS_DIR, 'avg_latency_comparison.png'), dpi=500, facecolor='white')
    plt.close()
    print("Created: ablation_results/avg_latency_comparison.png")

    # 3. Bar plot: Average Fidelity
    if 'avg_fidelity' in summary_df.columns and summary_df['avg_fidelity'].notna().any():
        plt.figure(figsize=(12, 7))
        pivot_fidelity = summary_df.pivot(index='algorithm', columns='ablation', values='avg_fidelity')[ablation_order]
        ax = pivot_fidelity.plot(kind='bar', rot=0, width=0.8, edgecolor='black', capsize=4)
        plt.title('Average Semantic Fidelity by Algorithm and Ablation', fontsize=16, fontweight='bold')
        plt.ylabel('Average Fidelity (%)', fontsize=14)
        plt.xlabel('Algorithm', fontsize=14)
        plt.ylim(0, 105)
        plt.legend(title='Ablation', fontsize=11, title_fontsize=12, loc='best')
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:.1f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=9, rotation=90)
        
        plt.savefig(os.path.join(RESULTS_DIR, 'avg_fidelity_comparison.png'), dpi=500, facecolor='white')
        plt.close()
        print("Created: ablation_results/avg_fidelity_comparison.png")

    # 4. Bar plot: Average Power Consumption (Log Scale)
    if 'avg_power' in summary_df.columns and summary_df['avg_power'].notna().any():
        plt.figure(figsize=(12, 7))
        pivot_power = summary_df.pivot(index='algorithm', columns='ablation', values='avg_power')[ablation_order]
        ax = pivot_power.plot(kind='bar', rot=0, width=0.8, edgecolor='black', capsize=4)
        plt.yscale('log')
        plt.title('Average Power Consumption by Algorithm and Ablation (Log Scale)', fontsize=16, fontweight='bold')
        plt.ylabel('Average Power (W, log scale)', fontsize=14)
        plt.xlabel('Algorithm', fontsize=14)
        plt.legend(title='Ablation', fontsize=11, title_fontsize=12, loc='best')
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7, which='both')
        
        # Add value labels
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:.1f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=9, rotation=90)
        
        plt.savefig(os.path.join(RESULTS_DIR, 'avg_power_comparison.png'), dpi=500, facecolor='white')
        plt.close()
        print("Created: ablation_results/avg_power_comparison.png")

    # 5. Bar plot: Total Migrations
    if 'total_migrations' in summary_df.columns and summary_df['total_migrations'].notna().any():
        plt.figure(figsize=(12, 7))
        pivot_migrations = summary_df.pivot(index='algorithm', columns='ablation', values='total_migrations')[ablation_order]
        ax = pivot_migrations.plot(kind='bar', rot=0, width=0.8, edgecolor='black', capsize=4)
        plt.title('Total Service Migrations by Algorithm and Ablation', fontsize=16, fontweight='bold')
        plt.ylabel('Total Migrations', fontsize=14)
        plt.xlabel('Algorithm', fontsize=14)
        plt.legend(title='Ablation', fontsize=11, title_fontsize=12, loc='best')
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=9, rotation=90)
        
        plt.savefig(os.path.join(RESULTS_DIR, 'total_migrations_comparison.png'), dpi=500, facecolor='white')
        plt.close()
        print("Created: ablation_results/total_migrations_comparison.png")

    # 6. Bar plot: Total Communication (Bytes)
    if 'total_bytes' in summary_df.columns and summary_df['total_bytes'].notna().any():
        plt.figure(figsize=(12, 7))
        pivot_bytes = summary_df.pivot(index='algorithm', columns='ablation', values='total_bytes')[ablation_order]
        ax = pivot_bytes.plot(kind='bar', rot=0, width=0.8, edgecolor='black', capsize=4)
        plt.title('Total Communication Overhead by Algorithm and Ablation', fontsize=16, fontweight='bold')
        plt.ylabel('Total Bytes Exchanged (MB)', fontsize=14)
        plt.xlabel('Algorithm', fontsize=14)
        plt.legend(title='Ablation', fontsize=11, title_fontsize=12, loc='best')
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:.1f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=9, rotation=90)
        
        plt.savefig(os.path.join(RESULTS_DIR, 'total_communication_comparison.png'), dpi=500, facecolor='white')
        plt.close()
        print("Created: ablation_results/total_communication_comparison.png")

def main():
    summary_df = collect_metrics()
    # Exclude 'no_optimization' ablation from all plots and summary comparisons
    filtered_df = summary_df[summary_df['ablation'] != 'no_optimization']
    if not filtered_df.empty:
        print('\n📊 Ablation Results Summary (excluding no_optimization):')
        print(filtered_df)
        filtered_df.to_csv(os.path.join(RESULTS_DIR, 'ablation_summary.csv'), index=False)
        print(f'\n✅ Saved summary to {os.path.join(RESULTS_DIR, "ablation_summary.csv")}')
        
        print('\n🎨 Generating comparison plots for all metrics...')
        plot_summary(filtered_df)
        print('\n✅ All graphs saved to ablation_results/ folder')
    else:
        print('❌ No ablation results found (after filtering no_optimization).')

if __name__ == '__main__':
    main()
