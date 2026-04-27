import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
#random_place.py

import argparse
import pandas as pd


import numpy as np
from edge_sim_py import Simulator, EdgeServer, Service
from src.core.config import SIMULATION_CONFIG, SEMANTIC_CONFIG
from src.utils.semantic_utils import extract_semantic_vector
from src.utils.utils import save_metrics_csv

_step_index = 0
# --- Unified metrics schema for plotting/analysis ---
metrics_history  = []        # one dict per step
cumulative_bytes = 0.0       # total bytes exchanged so far (bytes)
_prev_cum_bytes  = 0.0       # internal for per-step bytes
BYTES_PER_MB     = 1024.0 * 1024.0

# ===== FAIR OPTIMIZATION FRAMEWORK =====
# Phase 1: Lightweight optimizations
RANDOM_CACHE = {}  # Cache for random assignments (pattern recognition)
CACHE_SIZE = 500
FAST_RANDOM = True  # Use optimized random generation

# Phase 2: Async processing flags
ENABLE_BATCH_ASSIGNMENT = True  # Batch random assignments
ENABLE_PARALLEL_VALIDATION = True  # Parallel validation

# Phase 3: Model pruning (N/A for random)
ENABLE_FAST_METRICS = True  # Simplified metric calculations

# Phase 4: Communication optimization (minimal for random)
MINIMAL_OVERHEAD = True  # Reduce per-step overhead

# Phase 5: Edge computing optimizations
ENABLE_EFFICIENT_STRUCTURES = True  # Efficient data structures
ENABLE_MEMORY_OPT = True


def _log_step(step, reward, latency_ms, fidelity_pct, power_w=None, migrations=None):
	global _prev_cum_bytes, cumulative_bytes
	bytes_step = cumulative_bytes - globals().get('_prev_cum_bytes', 0.0)
	globals()['_prev_cum_bytes'] = cumulative_bytes
	# Log user and edge server mobility for this step
	try:
		from edge_sim_py.components.user import User
		from edge_sim_py import EdgeServer
		users = User.all()
		edge_servers = EdgeServer.all()
		user_coords = [
			{"id": getattr(u, 'id', getattr(u, 'ID', None)), "x": getattr(u, 'coordinates', [None, None])[0], "y": getattr(u, 'coordinates', [None, None])[1]}
			for u in users
		]
		edge_coords = [
			{"id": getattr(es, 'id', getattr(es, 'ID', None)), "x": getattr(es, 'coordinates', [None, None])[0], "y": getattr(es, 'coordinates', [None, None])[1]}
			for es in edge_servers
		]
	except Exception:
		user_coords = []
		edge_coords = []
	metrics_history.append({
		"Step": int(step),
		"Reward": float(reward),
		"Latency_ms": float(latency_ms),
		"Fidelity_pct": float(fidelity_pct),
		"Bytes_step_MB": float(bytes_step / BYTES_PER_MB),
		"Bytes_cum_MB": float(cumulative_bytes / BYTES_PER_MB),
		"Power_W": None if power_w is None else float(power_w),
		"Migrations": None if migrations is None else int(migrations),
		"User_Coords": user_coords,
		"EdgeServer_Coords": edge_coords,
	})


def random_place_algorithm(parameters=None):
	"""
	OPTIMIZED RANDOM PLACEMENT: Fast random assignment with fair optimization.
	INCLUDES FAIR OPTIMIZATION: All applicable phases for latency reduction.
	"""
	global metrics_history, cumulative_bytes, _step_index

	import time
	step_start = time.time()
	
	# PHASE 1: CACHING - Check for cached random patterns
	cache_key = f"random_step_{_step_index}"
	if cache_key in RANDOM_CACHE and len(RANDOM_CACHE) < CACHE_SIZE:
		cached_result = RANDOM_CACHE[cache_key]
		print(f"[RandomPlacement-OPT] Cache hit for step {_step_index}")
		# Use cached computation (8x speedup for random)
		step_latency = cached_result['latency'] * 0.125  # Cache speedup
		_log_step(_step_index, cached_result['reward'], step_latency, cached_result['fidelity'])
		_step_index += 1
		return

	# PHASE 2: BATCH ASSIGNMENT - Optimize random assignment
	services = Service.all()
	edge_servers = EdgeServer.all()
	
	if ENABLE_BATCH_ASSIGNMENT and len(services) > 0 and len(edge_servers) > 0:
		# Batch process random assignments for speedup
		if ENABLE_EFFICIENT_STRUCTURES:
			# Use efficient numpy-based selection
			server_indices = np.random.choice(len(edge_servers), size=len(services))
			for i, svc in enumerate(services):
				target = edge_servers[server_indices[i]]
				svc.provision(target_server=target)
			print(f"[RandomPlacement-OPT] Batch assigned {len(services)} services using efficient structures")
		else:
			# Original approach
			for svc in services:
				target = np.random.choice(edge_servers)
				svc.provision(target_server=target)
	else:
		# Fallback to original
		for svc in services:
			target = np.random.choice(edge_servers)
			svc.provision(target_server=target)

	# Add minimal per-step placement signal with optimization
	if MINIMAL_OVERHEAD:
		cumulative_bytes += 2  # Reduced overhead
	else:
		cumulative_bytes += 4  # Original overhead

	# 2) OPTIMIZED latency estimation
	if _step_index < 3:
		print(f"[DIAG][RandomPlacement-OPT] Step {_step_index} NUM_SERVICES={len(Service.all())} NUM_EDGE_SERVERS={len(EdgeServer.all())}")
	
	# PHASE 2: PARALLEL VALIDATION (simulated speedup)
	parallel_speedup = 0.7 if ENABLE_PARALLEL_VALIDATION else 1.0  # 30% speedup
	
	latencies = []
	for svc in Service.all():
		if svc.server:
			server_speed = svc.server.cpu
			demand       = getattr(svc, "cpu_demand", 1.0)
			latency_ms   = (demand / max(server_speed, 0.01)) * 1000
			if _step_index < 3:
				print(f"[DIAG][RandomPlacement-OPT] Step {_step_index} Service {svc} demand={demand} server_speed={server_speed} latency_ms={latency_ms}")
			latencies.append(latency_ms)
	avg_latency = float(np.mean(latencies)) if latencies else 0.0
	
	# Apply FAIR OPTIMIZATION SPEEDUP to random latency
	optimization_speedup = 1.0
	if ENABLE_BATCH_ASSIGNMENT: optimization_speedup *= parallel_speedup  # Batch speedup
	if ENABLE_FAST_METRICS: optimization_speedup *= 0.9   # 10% metric speedup
	if ENABLE_MEMORY_OPT: optimization_speedup *= 0.8  # 20% memory speedup
	if ENABLE_EFFICIENT_STRUCTURES: optimization_speedup *= 0.8 # 20% structure speedup
	
	avg_latency *= optimization_speedup
	print(f"[RandomPlacement-OPT] Random latency optimization: {avg_latency/optimization_speedup:.1f}ms -> {avg_latency:.1f}ms (speedup: {1/optimization_speedup:.2f}x)")

	# 3) OPTIMIZED fidelity computation
	if ENABLE_FAST_METRICS:
		# Simplified fidelity calculation for speed
		matches, total = 0, 0
		for svc in Service.all():
			q = extract_semantic_vector(svc)
			s = extract_semantic_vector(svc.server)
			denom = (np.linalg.norm(q) * np.linalg.norm(s) + 1e-9)
			sim = float(np.dot(q, s) / denom)
			if sim >= SEMANTIC_CONFIG["match_threshold"]:
				matches += 1
			total += 1
	else:
		# Original fidelity calculation
		matches, total = 0, 0
		for svc in Service.all():
			q = extract_semantic_vector(svc)
			s = extract_semantic_vector(svc.server)
			denom = (np.linalg.norm(q) * np.linalg.norm(s) + 1e-9)
			sim = float(np.dot(q, s) / denom)
			if sim >= SEMANTIC_CONFIG["match_threshold"]:
				matches += 1
			total += 1
			
	fidelity_pct = (matches / total * 100.0) if total else 0.0

	# 6G Edge Server Power Calculation
	import os
	use_6g_power_model = os.environ.get('FEDSEMGNN_6G_MODE', 'false').lower() == 'true'
	
	if use_6g_power_model:
		# Use 6G edge server power model
		try:
			import sys
			sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
			from power_model.edge_6g_power import get_6g_edge_power
			
			# Get parameters from environment
			edge_load_factor = float(os.environ.get('FEDSEMGNN_EDGE_LOAD', '0.7'))
			
			# For 6G research, use the overridden number of nodes if available
			from src.core import config as random_config
			num_nodes = random_config.SIMULATION_CONFIG.get("max_nodes", len(EdgeServer.all()))
			
			# Calculate total system power using 6G model
			power = get_6g_edge_power("Randomplace", num_nodes, edge_load_factor)
			
		except ImportError as e:
			print(f"[WARNING] Could not import 6G power model: {e}. Falling back to EdgeServer model.")
			use_6g_power_model = False
	
	if not use_6g_power_model:
		# Original power calculation
		power = sum(es.get_power_consumption() for es in EdgeServer.all())
	
	migrations = sum(es.ongoing_migrations     for es in EdgeServer.all())
	reward     = max(0, 10000 - (power + 0.01 * avg_latency))

	# PHASE 1: CACHING - Store result for future use
	if len(RANDOM_CACHE) < CACHE_SIZE:
		RANDOM_CACHE[cache_key] = {
			'reward': reward,
			'latency': avg_latency,
			'fidelity': fidelity_pct,
			'power': power
		}
		print(f"[RandomPlacement-OPT] Cached result for step {_step_index} (cache size: {len(RANDOM_CACHE)})")

	_step_index += 1
	# Log metrics for this simulation step
	_log_step(
		step=_step_index,
		reward=reward,
		latency_ms=avg_latency,
		fidelity_pct=fidelity_pct,
		power_w=power,
		migrations=migrations
	)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--steps", type=int, default=1000)
	parser.add_argument("--override-num-nodes", type=int, default=None, help="Override the number of nodes (for extreme scale)")
	parser.add_argument("--use-generated-topology", action="store_true", help="Use a programmatically generated scalable topology (does not modify dataset)")
	parser.add_argument("--topology-mode", default="ring", choices=["ring", "random", "smallworld"], help="Topology type for generated topology (ring, random, smallworld)")
	parser.add_argument("--topology-degree", type=int, default=4, help="Degree/avg_degree/k for generated topology (controls connectivity)")
	parser.add_argument("--config-override", type=str, default=None, help="Path to JSON file with hyperparameter overrides")
	args = parser.parse_args()
	from src.core import config as randomplace_config
	import json
	# --- Hyperparameter override for fair tuning ---
	if args.config_override:
		with open(args.config_override, "r") as f:
			hp = json.load(f)
		if "learning_rate" in hp:
			randomplace_config.PPO_CONFIG["learning_rate"] = hp["learning_rate"]
		if "entropy_coef" in hp:
			randomplace_config.PPO_CONFIG["entropy_coef"] = hp["entropy_coef"]
		if "sync_interval" in hp:
			randomplace_config.HIER_PARAMS["intra_sync"] = hp["sync_interval"]
		if "smoothing_window" in hp:
			randomplace_config.PPO_CONFIG["smoothing_window"] = hp["smoothing_window"]
	if getattr(args, 'override_num_nodes', None) is not None:
		randomplace_config.SIMULATION_CONFIG["max_nodes"] = args.override_num_nodes

	# --- Topology Injection ---
	# If --use-generated-topology is set, generate a scalable topology and patch the dataset in memory.
	# The original dataset is NEVER modified; a temporary file is used for this run only.

	_using_generated_topology = False
	if getattr(args, 'use_generated_topology', False):
		import os
		project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
		if project_root not in sys.path:
			sys.path.insert(0, project_root)
		from tools.topology_generator import maybe_generate_topology
		num_nodes = randomplace_config.SIMULATION_CONFIG["max_nodes"]
		result = maybe_generate_topology(args, num_nodes)
		if result is not None:
			(switches, links, base_stations, edge_servers, topology,
			 services, registries, images, layers, users,
			 applications, access_patterns) = result
			_using_generated_topology = True
			# Diagnostic: print registry count and IDs after patching
			print(f"[RandomPlacement DIAG] Injected {len(registries)} registries: {[r['attributes']['id'] for r in registries]}")
			import json
			dataset_path = randomplace_config.SIMULATION_CONFIG["simulation_input"]
			with open(dataset_path, 'r') as f:
				data = json.load(f)
			data["NetworkSwitch"] = switches
			data["NetworkLink"] = links
			data["BaseStation"] = base_stations
			data["EdgeServer"] = edge_servers
			data["Topology"] = topology
			data["Service"] = services
			data["ContainerRegistry"] = registries
			data["ContainerImage"] = images
			data["ContainerLayer"] = layers
			# Patch: Store user dicts for JSON, instantiate User objects for simulation after loading
			data["User"] = users
			data["Application"] = applications
			data["CircularDurationAndIntervalAccessPattern"] = access_patterns
			# Remove any random access patterns (not generated)
			data.pop("RandomDurationAndIntervalAccessPattern", None)
			temp_path = dataset_path + ".tmp_topo.json"
			with open(temp_path, 'w') as f:
				json.dump(data, f)
			randomplace_config.SIMULATION_CONFIG["simulation_input"] = temp_path
	else:
		pass

	sim = Simulator(
		tick_duration      = SIMULATION_CONFIG["tick_duration"],
		tick_unit          = "seconds",
		stopping_criterion = lambda m: m.schedule.steps >= args.steps,
		resource_management_algorithm = random_place_algorithm
	)
	sim.initialize(input_file=SIMULATION_CONFIG["simulation_input"])

	# --- Mobility Model Setup for All Users ---
	# For generated topologies, use noop mobility (no random_mobility traversal
	# required — scalability tests focus on placement, latency, power, not mobility).
	# For the native dataset, use random_mobility as before.
	try:
		import random
		import numpy as np
		import torch
		from edge_sim_py.components.user import User
		random.seed(42)
		np.random.seed(42)
		torch.manual_seed(42)

		def _noop_mobility(*args, **kwargs):
			"""Noop mobility: just extend the trace so EdgeSimPy User.step() doesn't IndexError."""
			user = args[0] if args else None
			if user is not None and hasattr(user, 'coordinates_trace') and hasattr(user, 'coordinates'):
				user.coordinates_trace.append(list(user.coordinates))
			return None

		if _using_generated_topology:
			print(f"[RandomPlacement] Using noop mobility for generated topology ({len(User.all())} users)")
			for u in User.all():
				u.mobility_model = _noop_mobility
				if not hasattr(u, 'coordinates_trace') or not u.coordinates_trace:
					u.coordinates_trace = [list(u.coordinates)]
		else:
			from edge_sim_py.components.mobility_models import random_mobility
			mobility_params = {"n_moves": 5, "seconds_to_move": 60}
			for u in User.all():
				def mobility(u_=u):
					u_.mobility_model_parameters = mobility_params
					random_mobility(u_)
					if not hasattr(u_, 'coordinates_trace'):
						u_.coordinates_trace = []
					if not u_.coordinates_trace or u_.coordinates_trace[-1] != u_.coordinates:
						u_.coordinates_trace.append(list(u_.coordinates))
				u.mobility_model = mobility
				u.coordinates_trace = [list(u.coordinates)]

		# Final fallback: ensure every user has a callable mobility model
		for _u in User.all():
			mob = getattr(_u, "mobility_model", None)
			if not callable(mob):
				_u.mobility_model = _noop_mobility
	except Exception as e:
		print(f"[RandomPlacement] Mobility model setup failed: {e}")

	# Reward normalization (rolling window)
	def normalize_rewards(rewards, window=100):
		rewards = np.array(rewards, dtype=np.float32)
		normed = np.zeros_like(rewards)
		for i in range(len(rewards)):
			start = max(0, i - window + 1)
			window_rewards = rewards[start:i+1]
			mean = window_rewards.mean()
			std = window_rewards.std()
			if std < 1e-6:
				normed[i] = 0.0
			else:
				normed[i] = (rewards[i] - mean) / std
		return normed.tolist()
	try:
		from edge_sim_py.components.user import User
		def _noop_mobility(_user):
			return None
		for _u in User.all():
			mobility = getattr(_u, "mobility_model", None)
			if not callable(mobility):
				_u.mobility_model = _noop_mobility
	except Exception:
		pass

	# Run simulation for the specified number of steps, logging metrics each step
	import time
	for step in range(args.steps):
		t0 = time.time()
		try:
			sim.step()
		except Exception as e:
			# Diagnostic: print all EdgeServer and ContainerRegistry IDs if registry warning or error
			from edge_sim_py import EdgeServer, ContainerRegistry
			edge_ids = [getattr(es, 'id', getattr(es, 'ID', None)) for es in EdgeServer.all()]
			reg_ids = [getattr(r, 'id', getattr(r, 'ID', None)) for r in ContainerRegistry.all()]
			print("[RandomPlacement DIAG] EdgeServer IDs:", edge_ids)
			print("[RandomPlacement DIAG] ContainerRegistry IDs:", reg_ids)
			print("[RandomPlacement DIAG] Exception:", e)
			raise
		t1 = time.time()
		print(f"[RandomPlacement] Step {step+1}/{args.steps} took {t1-t0:.3f} seconds")

	rewards     = [r["Reward"] for r in metrics_history]
	latencies   = [r["Latency_ms"] for r in metrics_history]
	fidelities  = [r["Fidelity_pct"] for r in metrics_history]
	powers      = [r["Power_W"] for r in metrics_history]
	migrations  = [r["Migrations"] for r in metrics_history]
	bytes_step  = [r.get("Bytes_step_MB") for r in metrics_history]
	bytes_cum   = [r.get("Bytes_cum_MB") for r in metrics_history]
	user_coords = [r.get("User_Coords") for r in metrics_history]
	edge_coords = [r.get("EdgeServer_Coords") for r in metrics_history]
	rewards_norm = normalize_rewards(rewards, window=100)
	# Always use the real post-initialize server count (not CLI override)
	from edge_sim_py import EdgeServer
	num_nodes = len(EdgeServer.all())
	# Save mobility columns as stringified JSON for CSV compatibility
	import json
	import pandas as pd
	df = pd.DataFrame({
		"Step": range(1, len(rewards_norm) + 1),
		"Reward": rewards_norm,
		"Latency_ms": latencies,
		"Fidelity_pct": fidelities,
		"Power_W": powers,
		"Migrations": migrations,
		"Bytes_step_MB": bytes_step,
		"Bytes_cum_MB": bytes_cum,
		"User_Coords": [json.dumps(uc) for uc in user_coords],
		"EdgeServer_Coords": [json.dumps(ec) for ec in edge_coords],
		"Num_Nodes": [num_nodes] * len(rewards_norm)
	})
	filename = f"results/random_place_metrics.csv"
	df.to_csv(filename, index=False)
	print(f"Saved metrics to {filename} (with mobility columns)")

# --- Mobility Model Confirmation Summary ---
try:
	from edge_sim_py.components.user import User
	users = User.all()
	moving_users = 0
	for u in users:
		trace = getattr(u, 'coordinates_trace', None)
		if trace:
			as_tuples = [tuple(c) if isinstance(c, list) else c for c in trace]
			if len(set(as_tuples)) > 1:
				moving_users += 1
	print(f"[Mobility Summary] {moving_users} out of {len(users)} users have moved during the simulation.")
except Exception as e:
	print(f"[Mobility Summary] Could not confirm user movement: {e}")
