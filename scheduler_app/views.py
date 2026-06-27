from django.shortcuts import render

# Create your views here.
from typing import List, Dict, Tuple


def scale_tasks(tasks: List[Dict], time_unit: float = 0.25):
    multiplier = round(1 / time_unit)
    scaled = []
    for idx, t in enumerate(tasks):
        duration = float(t.get('durationHours') or t.get('duration') or 0)
        score = float(t.get('score') or t.get('impact') or t.get('Impact') or 0)
        tid = t.get('id') or t.get('TaskID') or f't{idx}'
        weight = max(0, int(round(duration * multiplier)))
        scaled.append({'idx': idx, 'id': tid, 'durationHours': duration, 'score': score, 'weight': weight})
    return scaled, multiplier


def exact_knapsack_by_capacity(tasks: List[Dict], capacity_units: int) -> Tuple[List[Dict], int, float]:
    n = len(tasks)
    dp = [0] * (capacity_units + 1)
    pick = [-1] * (capacity_units + 1)

    for i, item in enumerate(tasks):
        w = item['weight']
        v = int(round(item['score']))
        if w <= 0:
            for c in range(capacity_units + 1):
                dp[c] += v
            continue
        for c in range(capacity_units, w - 1, -1):
            cand = dp[c - w] + v
            if cand > dp[c]:
                dp[c] = cand
                pick[c] = i

    # reconstruct
    c = capacity_units
    chosen = [False] * n
    while c > 0:
        i = pick[c]
        if i == -1:
            break
        if chosen[i]:
            break
        chosen[i] = True
        c -= tasks[i]['weight']

    picks = []
    total_weight = 0
    total_score = 0
    for i in range(n):
        if chosen[i]:
            picks.append(tasks[i])
            total_weight += tasks[i]['weight']
            total_score += tasks[i]['score']

    return picks, total_weight, total_score


def greedy_knapsack(tasks: List[Dict], capacity_units: int) -> Tuple[List[Dict], int, float]:
    pickable = [t for t in tasks]
    pickable.sort(key=lambda x: (x['score'] / (x['weight'] or 1e-9)), reverse=True)
    picks = []
    used = 0
    value = 0
    for t in pickable:
        if used + t['weight'] <= capacity_units:
            picks.append(t)
            used += t['weight']
            value += t['score']

    # small local improvement for modest sizes
    if len(tasks) <= 500:
        remaining = [t for t in pickable if t not in picks]
        for i in range(len(picks)):
            for j in range(len(remaining)):
                p = picks[i]
                r = remaining[j]
                if used - p['weight'] + r['weight'] <= capacity_units and value - p['score'] + r['score'] > value:
                    used = used - p['weight'] + r['weight']
                    value = value - p['score'] + r['score']
                    picks[i] = r
                    remaining[j] = p

    return picks, used, value


def schedule(tasks_raw: List[Dict], capacity_hours: float, time_unit: float = 0.25, max_dp_states: int = int(5e7)):
    scaled, multiplier = scale_tasks(tasks_raw, time_unit)
    capacity_units = max(0, int(round(capacity_hours * multiplier)))
    cost = capacity_units * len(scaled)
    if cost > 0 and cost <= max_dp_states:
        picks, total_weight, total_score = exact_knapsack_by_capacity(scaled, capacity_units)
    else:
        picks, total_weight, total_score = greedy_knapsack(scaled, capacity_units)

    result_picks = [{'id': p['id'], 'durationHours': p['durationHours'], 'score': p['score'], 'weightUnits': p['weight']} for p in picks]
    return {
        'picks': result_picks,
        'totalScore': total_score,
        'totalDurationHours': total_weight / multiplier,
        'usedUnits': total_weight,
        'capacityUnits': capacity_units,
        'timeUnit': time_unit,
    }
