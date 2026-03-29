import math
from typing import Dict, List


def summarize_stats(values: List[float]) -> Dict[str, float]:
    """Compute summary statistics for a numeric list.

    Returns a dictionary with keys 'count', 'min', 'max', 'mean', 'median',
    and 'std_dev' as floats. For an empty input all values are 0.0.
    
    Args:
        values: A list of float numbers.

    Returns:
        Dictionary mapping each statistic to its computed value.
    """
    try:
        count = len(values)
        if count == 0:
            return {'count': 0.0, 'min': 0.0, 'max': 0.0,
                    'mean': 0.0, 'median': 0.0, 'std_dev': 0.0}

        mean = sum(values) / count
        # Sample standard deviation (n-1 denominator)
        variance = sum((x - mean) ** 2 for x in values) / (count - 1)
        std_dev = math.sqrt(variance) if count > 1 else 0.0

        sorted_vals = sorted(values)
        if count % 2 == 1:
            median = float(sorted_vals[count // 2])
        else:
            median = (sorted_vals[count // 2 - 1] + sorted_vals[count // 2]) / 2.0

        min_val = float(sorted_vals[0])
        max_val = float(sorted_vals[-1])

        return {
            'count': float(count),
            'min': min_val,
            'max': max_val,
            'mean': mean,
            'median': median,
            'std_dev': std_dev
        }
    except Exception:
        # Graceful fallback: return zeros on any unexpected error
        return {'count': 0.0, 'min': 0.0, 'max': 0.0,
                'mean': 0.0, 'median': 0.0, 'std_dev': 0.0}
