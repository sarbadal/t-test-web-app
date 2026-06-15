"""TTest Analysis model for storing statistical analysis results."""

import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from enum import Enum

from .base import Base, db


class TestType(Enum):
    """Enum for different types of t-tests."""
    ONE_SAMPLE = "one_sample"
    TWO_SAMPLE = "two_sample"
    PAIRED = "paired"


class SignificanceLevel(Enum):
    """Common significance levels for statistical tests."""
    ALPHA_001 = 0.01
    ALPHA_005 = 0.05
    ALPHA_010 = 0.10


class TTestAnalysis(Base):
    """Model for storing t-test analysis results."""
    
    __tablename__ = 'ttest_analyses'
    
    # Analysis metadata
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Test configuration
    test_type = Column(SQLEnum(TestType), nullable=False)
    confidence_level = Column(Float, nullable=False, default=0.95)
    significance_level = Column(Float, nullable=False, default=0.05)
    
    # Statistical results
    t_statistic = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    degrees_of_freedom = Column(Integer, nullable=True)
    
    # Sample statistics
    sample_size = Column(Integer, nullable=False)
    sample_mean = Column(Float, nullable=True)  # For one-sample tests
    mean_difference = Column(Float, nullable=True)  # For paired and two-sample tests
    
    # Effect size and additional statistics
    cohens_d = Column(Float, nullable=True)  # Effect size
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    
    # Test interpretation
    is_significant = Column(Boolean, nullable=False)
    interpretation = Column(Text, nullable=True)
    
    # Raw results storage
    raw_results = Column(JSON, nullable=True)  # Store complete results as JSON
    
    # Relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="analyses")
    
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    dataset = relationship("DataSet", back_populates="analyses")
    
    def __init__(self, test_type, confidence_level, user_id, dataset_id, **kwargs):
        """Initialize analysis with basic parameters."""
        self.test_type = test_type
        self.confidence_level = confidence_level
        self.significance_level = 1 - confidence_level
        self.user_id = user_id
        self.dataset_id = dataset_id
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_results(self, results_dict):
        """Set analysis results from dictionary."""
        # Extract main statistical results
        self.t_statistic = results_dict.get('t_statistic')
        self.p_value = results_dict.get('p_value')
        self.sample_size = results_dict.get('sample_size')
        
        # Set test-specific results
        if 'mean' in results_dict:
            self.sample_mean = results_dict['mean']
        if 'mean_difference' in results_dict:
            self.mean_difference = results_dict['mean_difference']
        
        # Determine significance
        self.is_significant = self.p_value < self.significance_level
        
        # Store complete results
        self.raw_results = results_dict
        
        # Generate interpretation
        self.interpretation = self._generate_interpretation()
    
    def _generate_interpretation(self):
        """Generate human-readable interpretation of results."""
        significance_text = "significant" if self.is_significant else "not significant"
        
        if self.test_type == TestType.ONE_SAMPLE:
            return (f"The one-sample t-test shows that the sample mean "
                   f"({self.sample_mean:.4f}) is {significance_text} "
                   f"(p = {self.p_value:.6f}, α = {self.significance_level:.3f}).")
        
        elif self.test_type == TestType.TWO_SAMPLE:
            return (f"The two-sample t-test shows that the difference between "
                   f"groups is {significance_text} "
                   f"(mean difference = {self.mean_difference:.4f}, "
                   f"p = {self.p_value:.6f}, α = {self.significance_level:.3f}).")
        
        elif self.test_type == TestType.PAIRED:
            return (f"The paired t-test shows that the difference between "
                   f"conditions is {significance_text} "
                   f"(mean difference = {self.mean_difference:.4f}, "
                   f"p = {self.p_value:.6f}, α = {self.significance_level:.3f}).")
        
        return "Analysis completed."
    
    def calculate_effect_size(self, data):
        """Calculate Cohen's d effect size."""
        import numpy as np
        
        if self.test_type == TestType.ONE_SAMPLE:
            # Cohen's d for one-sample test
            sample_data = np.array(data['data'])
            d = np.mean(sample_data) / np.std(sample_data, ddof=1)
            
        elif self.test_type == TestType.TWO_SAMPLE:
            # Cohen's d for independent samples
            group1 = np.array(data['group1'])
            group2 = np.array(data['group2'])
            
            n1, n2 = len(group1), len(group2)
            s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
            
            # Pooled standard deviation
            pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
            d = (np.mean(group1) - np.mean(group2)) / pooled_std
            
        elif self.test_type == TestType.PAIRED:
            # Cohen's d for paired samples
            before = np.array(data['before'])
            after = np.array(data['after'])
            differences = after - before
            d = np.mean(differences) / np.std(differences, ddof=1)
        
        self.cohens_d = float(d)
        return d
    
    def get_effect_size_interpretation(self):
        """Get interpretation of effect size."""
        if self.cohens_d is None:
            return "Effect size not calculated"
        
        abs_d = abs(self.cohens_d)
        if abs_d < 0.2:
            return "Very small effect"
        elif abs_d < 0.5:
            return "Small effect"
        elif abs_d < 0.8:
            return "Medium effect"
        else:
            return "Large effect"
    
    def to_dict(self, include_raw=False):
        """Convert analysis to dictionary."""
        analysis_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'test_type': self.test_type.value if self.test_type else None,
            'confidence_level': self.confidence_level,
            'significance_level': self.significance_level,
            't_statistic': self.t_statistic,
            'p_value': self.p_value,
            'degrees_of_freedom': self.degrees_of_freedom,
            'sample_size': self.sample_size,
            'sample_mean': self.sample_mean,
            'mean_difference': self.mean_difference,
            'cohens_d': self.cohens_d,
            'confidence_interval_lower': self.confidence_interval_lower,
            'confidence_interval_upper': self.confidence_interval_upper,
            'is_significant': self.is_significant,
            'interpretation': self.interpretation,
            'effect_size_interpretation': self.get_effect_size_interpretation(),
            'user_id': self.user_id,
            'dataset_id': self.dataset_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        if include_raw:
            analysis_dict['raw_results'] = self.raw_results
            
        return analysis_dict
    
    @classmethod
    def create_from_results(cls, results_dict, user_id, dataset_id, name=None):
        """Create analysis instance from results dictionary."""
        # Determine test type from results
        test_type_str = results_dict.get('test_type', '')
        if 'One-sample' in test_type_str:
            test_type = TestType.ONE_SAMPLE
        elif 'Two-sample' in test_type_str:
            test_type = TestType.TWO_SAMPLE
        elif 'Paired' in test_type_str:
            test_type = TestType.PAIRED
        else:
            raise ValueError(f"Unknown test type: {test_type_str}")
        
        # Create analysis instance
        analysis = cls(
            test_type=test_type,
            confidence_level=results_dict.get('confidence_level', 0.95),
            user_id=user_id,
            dataset_id=dataset_id,
            name=name
        )
        
        # Set results
        analysis.set_results(results_dict)
        
        return analysis
    
    def __repr__(self):
        """Return string representation of the analysis."""
        return f"<TTestAnalysis(id={self.id}, type={self.test_type.value if self.test_type else 'None'}, p={self.p_value})>"