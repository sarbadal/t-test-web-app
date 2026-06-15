"""Dataset service for handling data upload and management."""

import json
from typing import Dict, Any, List, Optional
from flask import current_app

from ..models import DataSet, db


class DataSetService:
    """Service class for managing datasets."""
    
    @staticmethod
    def create_dataset(name: str, data: Dict[str, Any], original_filename: str, 
                      user_id: int, description: str = None) -> DataSet:
        """Create and save a new dataset."""
        try:
            # Validate data structure
            DataSetService._validate_data_structure(data)
            
            # Create dataset instance
            dataset = DataSet(
                name=name,
                data=data,
                original_filename=original_filename,
                user_id=user_id,
                description=description
            )
            
            # Calculate file size (approximate)
            dataset.file_size = len(json.dumps(data).encode('utf-8'))
            
            # Save to database
            db.session.add(dataset)
            db.session.commit()
            
            current_app.logger.info(f"Dataset created successfully: {dataset.id}")
            return dataset
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating dataset: {str(e)}")
            raise
    
    @staticmethod
    def _validate_data_structure(data: Dict[str, Any]) -> None:
        """Validate that the data structure is appropriate for t-test analysis."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # Check for valid data structures
        valid_structures = [
            'data' in data,  # One-sample
            'before' in data and 'after' in data,  # Paired
            'group1' in data and 'group2' in data,  # Two-sample
        ]
        
        if not any(valid_structures):
            raise ValueError(
                "Invalid data structure. Must contain 'data', 'before'/'after', or 'group1'/'group2'"
            )
        
        # Validate data types and sizes
        if 'data' in data:
            if not isinstance(data['data'], list) or len(data['data']) == 0:
                raise ValueError("One-sample data must be a non-empty list")
                
        elif 'before' in data and 'after' in data:
            before, after = data['before'], data['after']
            if not isinstance(before, list) or not isinstance(after, list):
                raise ValueError("Paired data must be lists")
            if len(before) != len(after):
                raise ValueError("Paired data must have equal lengths")
            if len(before) == 0:
                raise ValueError("Paired data cannot be empty")
                
        elif 'group1' in data and 'group2' in data:
            group1, group2 = data['group1'], data['group2']
            if not isinstance(group1, list) or not isinstance(group2, list):
                raise ValueError("Two-sample data must be lists")
            if len(group1) == 0 or len(group2) == 0:
                raise ValueError("Two-sample groups cannot be empty")
    
    @staticmethod
    def get_user_datasets(user_id: int, limit: int = 50) -> List[DataSet]:
        """Get datasets for a specific user."""
        return db.session.query(DataSet).filter_by(user_id=user_id)\
                         .order_by(DataSet.created_at.desc())\
                         .limit(limit).all()
    
    @staticmethod
    def get_dataset_by_id(dataset_id: int, user_id: int = None) -> Optional[DataSet]:
        """Get dataset by ID, optionally filtered by user."""
        query = db.session.query(DataSet).filter_by(id=dataset_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def delete_dataset(dataset_id: int, user_id: int) -> bool:
        """Delete a dataset if it belongs to the user."""
        dataset = db.session.query(DataSet).filter_by(
            id=dataset_id, user_id=user_id
        ).first()
        
        if dataset:
            # Check if dataset is used in any analyses
            if dataset.analyses.count() > 0:
                raise ValueError("Cannot delete dataset that is used in analyses")
            
            db.session.delete(dataset)
            db.session.commit()
            current_app.logger.info(f"Dataset deleted: {dataset_id}")
            return True
        return False
    
    @staticmethod
    def update_dataset(dataset_id: int, user_id: int, name: str = None, 
                      description: str = None) -> Optional[DataSet]:
        """Update dataset metadata."""
        dataset = db.session.query(DataSet).filter_by(
            id=dataset_id, user_id=user_id
        ).first()
        
        if dataset:
            if name is not None:
                dataset.name = name
            if description is not None:
                dataset.description = description
                
            db.session.commit()
            current_app.logger.info(f"Dataset updated: {dataset_id}")
            return dataset
        return None
    
    @staticmethod
    def get_dataset_summary(user_id: int) -> Dict[str, Any]:
        """Get summary statistics for user's datasets."""
        datasets = db.session.query(DataSet).filter_by(user_id=user_id).all()
        
        if not datasets:
            return {
                'total_datasets': 0,
                'dataset_type_counts': {},
                'total_size': 0,
                'latest_dataset': None
            }
        
        # Calculate summary statistics
        total_datasets = len(datasets)
        total_size = sum(d.file_size or 0 for d in datasets)
        
        # Count by dataset type
        dataset_type_counts = {}
        for dataset in datasets:
            dataset_type = dataset.dataset_type.value
            dataset_type_counts[dataset_type] = dataset_type_counts.get(dataset_type, 0) + 1
        
        # Get latest dataset
        latest_dataset = max(datasets, key=lambda d: d.created_at)
        
        return {
            'total_datasets': total_datasets,
            'dataset_type_counts': dataset_type_counts,
            'total_size': total_size,
            'average_size': total_size / total_datasets if total_datasets > 0 else 0,
            'latest_dataset': latest_dataset.to_dict() if latest_dataset else None
        }