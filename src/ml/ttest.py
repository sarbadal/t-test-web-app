import numpy as np
from scipy import stats

def perform_ttest(data, confidence_level):
    """Perform appropriate t-test based on data structure."""
    # One-sample t-test
    if 'data' in data:
        sample = np.array(data['data'])
        t_stat, p_value = stats.ttest_1samp(sample, 0)  # Test against mean = 0
        
        return {
            'test_type': 'One-sample t-test',
            'sample_size': len(sample),
            'confidence_level': confidence_level,
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'mean': float(np.mean(sample))
        }
    
    # Paired t-test
    elif 'before' in data and 'after' in data:
        before = np.array(data['before'])
        after = np.array(data['after'])
        
        if len(before) != len(after):
            raise ValueError("Before and after arrays must have the same length for paired t-test")
        
        t_stat, p_value = stats.ttest_rel(before, after)
        
        return {
            'test_type': 'Paired t-test',
            'sample_size': len(before),
            'confidence_level': confidence_level,
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'mean_difference': float(np.mean(after - before))
        }
    
    # Two-sample t-test
    elif 'group1' in data and 'group2' in data:
        group1 = np.array(data['group1'])
        group2 = np.array(data['group2'])
        
        t_stat, p_value = stats.ttest_ind(group1, group2)
        
        return {
            'test_type': 'Two-sample t-test',
            'sample_size': len(group1) + len(group2),
            'confidence_level': confidence_level,
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'mean_difference': float(np.mean(group1) - np.mean(group2))
        }
    
    raise ValueError("Invalid data format. Expected 'data', 'before'/'after', or 'group1'/'group2' keys")