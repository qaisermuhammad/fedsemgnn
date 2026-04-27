import os
import runpy
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


if __name__ == "__main__":
    # Configure FlatFedPPO to run as a centralized baseline.
    os.environ['FEDSEMGNN_CENTRALIZED'] = 'true'
    os.environ['FEDSEMGNN_METRICS_FILE'] = 'results/centralized_ppo_metrics.csv'

    # Execute FlatFedPPO as if it were run directly so it can parse sys.argv.
    runpy.run_path(
        os.path.join(project_root, 'src', 'algorithms', 'flat_fedppo.py'),
        run_name='__main__',
    )
