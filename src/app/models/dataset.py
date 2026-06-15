"""DataSet model for storing uploaded statistical data."""

import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from enum import Enum

from .base import Base, db


class DataSetType(Enum):
    """Enum for different types of statistical datasets."""
    ONE_SAMPLE = "one_sample"
    TWO_SAMPLE = "two_sample"  
    PAIRED = "paired"


class DataSet(Base):
    """Model for storing uploaded datasets and their metadata."""
    
    __tablename__ = 'datasets'
    
    # Basic dataset information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Dataset type and structure
    dataset_type = Column(SQLEnum(DataSetType), nullable=False)
    sample_size = Column(Integer, nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Data storage
    data_json = Column(JSON, nullable=False)  # Store the actual data as JSON
    data_checksum = Column(String(64), nullable=True)  # MD5 checksum for integrity
    
    # Relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="datasets")
    
    analyses = relationship("TTestAnalysis", back_populates="dataset", lazy="dynamic")
    
    def __init__(self, name, data, original_filename, user_id, description=None):
        """Initialize dataset with validation."""
        self.name = name
        self.original_filename = original_filename
        self.user_id = user_id
        self.description = description
        self.set_data(data)
    
    def set_data(self, data):
        """Set and validate the dataset data."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # Determine dataset type and sample size
        self.dataset_type, self.sample_size = self._analyze_data_structure(data)
        
        # Store the data as JSON
        self.data_json = data
        
        # Calculate checksum for data integrity
        self.data_checksum = self._calculate_checksum(data)
    
    def _analyze_data_structure(self, data):
        """Analyze the data structure to determine type and sample size."""
        if 'data' in data:
            # One-sample t-test
            sample_data = data['data']
            if not isinstance(sample_data, list):
                raise ValueError("One-sample data must be a list")
            return DataSetType.ONE_SAMPLE, len(sample_data)
        
        elif 'before' in data and 'after' in data:
            # Paired t-test
            before_data = data['before']
            after_data = data['after']
            if not isinstance(before_data, list) or not isinstance(after_data, list):
                raise ValueError("Paired data must be lists")
            if len(before_data) != len(after_data):
                raise ValueError("Paired data must have equal lengths")
            return DataSetType.PAIRED, len(before_data)
        
        elif 'group1' in data and 'group2' in data:
            # Two-sample t-test
            group1_data = data['group1']
            group2_data = data['group2']
            if not isinstance(group1_data, list) or not isinstance(group2_data, list):
                raise ValueError("Two-sample data must be lists")
            return DataSetType.TWO_SAMPLE, len(group1_data) + len(group2_data)
        
        else:
            raise ValueError("Invalid data structure. Must contain 'data', 'before'/'after', or 'group1'/'group2'")
    
    def _calculate_checksum(self, data):
        """Calculate MD5 checksum of the data for integrity checking."""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_data(self):
        """Get the dataset data."""
        return self.data_json
    
    def validate_integrity(self):
        """Validate data integrity using checksum."""
        current_checksum = self._calculate_checksum(self.data_json)
        return current_checksum == self.data_checksum
    
    def get_statistics(self):
        """Get basic statistics about the dataset."""
        import numpy as np
        
        stats = {
            'dataset_type': self.dataset_type.value,
            'sample_size': self.sample_size,
            'created_at': self.created_at.isoformat(),
        }
        
        if self.dataset_type == DataSetType.ONE_SAMPLE:
            data = np.array(self.data_json['data'])
            stats.update({
                'mean': float(np.mean(data)),
                'std': float(np.std(data, ddof=1)),
                'min': float(np.min(data)),
                'max': float(np.max(data)),
            })
        
        elif self.dataset_type == DataSetType.TWO_SAMPLE:
            group1 = np.array(self.data_json['group1'])
            group2 = np.array(self.data_json['group2'])
            stats.update({
                'group1_mean': float(np.mean(group1)),
                'group1_std': float(np.std(group1, ddof=1)),
                'group1_size': len(group1),
                'group2_mean': float(np.mean(group2)),
                'group2_std': float(np.std(group2, ddof=1)),
                'group2_size': len(group2),
            })
        
        elif self.dataset_type == DataSetType.PAIRED:
            before = np.array(self.data_json['before'])
            after = np.array(self.data_json['after'])
            diff = after - before
            stats.update({
                'before_mean': float(np.mean(before)),
                'after_mean': float(np.mean(after)),
                'mean_difference': float(np.mean(diff)),
                'difference_std': float(np.std(diff, ddof=1)),
            })
        
        return stats
    
    def to_dict(self, include_data=False):
        """Convert dataset to dictionary."""
        dataset_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dataset_type': self.dataset_type.value if self.dataset_type else None,
            'sample_size': self.sample_size,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'data_checksum': self.data_checksum,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        if include_data:
            dataset_dict['data'] = self.data_json
            
        return dataset_dict
    
    def __repr__(self):
        """Return string representation of the dataset."""
        return f"<DataSet(id={self.id}, name='{self.name}', type={self.dataset_type.value if self.dataset_type else 'None'})>"