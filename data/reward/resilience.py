def resilience_reward(sla_met_rate, recovery_lag, migrations):
    continuity_term = sla_met_rate
    recovery_term = max(0, 1.0 - recovery_lag/100.0)
    migration_penalty = -0.01 * migrations
    return continuity_term + recovery_term + migration_penalty
