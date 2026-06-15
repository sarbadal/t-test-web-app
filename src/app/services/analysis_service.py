"""Analysis service for handling statistical analysis business logic."""

from typing import Dict, Any, List, Optional
from flask import current_app

from ..models import TTestAnalysis, DataSet, db
from src.ml.ttest import perform_ttest


class AnalysisService:
    """Service class for managing statistical analyses."""
    
    @staticmethod
    def create_analysis(data: Dict[str, Any], confidence_level: float, 
                       user_id: int, dataset_id: int, name: str = None) -> TTestAnalysis:
        """Create and save a new t-test analysis."""
        try:
            # Perform the statistical analysis
            results = perform_ttest(data, confidence_level)
            
            # Create analysis record
            analysis = TTestAnalysis.create_from_results(
                results_dict=results,
                user_id=user_id,
                dataset_id=dataset_id,
                name=name
            )
            
            # Calculate effect size if dataset is available
            dataset = db.session.get(DataSet, dataset_id)
            if dataset:
                analysis.calculate_effect_size(dataset.get_data())
            
            # Save to database
            db.session.add(analysis)
            db.session.commit()
            
            current_app.logger.info(f"Analysis created successfully: {analysis.id}")
            return analysis
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating analysis: {str(e)}")
            raise
    
    @staticmethod
    def get_user_analyses(user_id: int, limit: int = 50) -> List[TTestAnalysis]:
        """Get analyses for a specific user."""
        return db.session.query(TTestAnalysis).filter_by(user_id=user_id)\
                         .order_by(TTestAnalysis.created_at.desc())\
                         .limit(limit).all()
    
    @staticmethod
    def get_analysis_by_id(analysis_id: int, user_id: int = None) -> Optional[TTestAnalysis]:
        """Get analysis by ID, optionally filtered by user."""
        query = db.session.query(TTestAnalysis).filter_by(id=analysis_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def delete_analysis(analysis_id: int, user_id: int) -> bool:
        """Delete an analysis if it belongs to the user."""
        analysis = db.session.query(TTestAnalysis).filter_by(
            id=analysis_id, user_id=user_id
        ).first()
        
        if analysis:
            db.session.delete(analysis)
            db.session.commit()
            current_app.logger.info(f"Analysis deleted: {analysis_id}")
            return True
        return False
    
    @staticmethod
    def get_analysis_summary(user_id: int) -> Dict[str, Any]:
        """Get summary statistics for user's analyses."""
        analyses = db.session.query(TTestAnalysis).filter_by(user_id=user_id).all()
        
        if not analyses:
            return {
                'total_analyses': 0,
                'significant_analyses': 0,
                'test_type_counts': {},
                'latest_analysis': None
            }
        
        # Calculate summary statistics
        total_analyses = len(analyses)
        significant_analyses = sum(1 for a in analyses if a.is_significant)
        
        # Count by test type
        test_type_counts = {}
        for analysis in analyses:
            test_type = analysis.test_type.value
            test_type_counts[test_type] = test_type_counts.get(test_type, 0) + 1
        
        # Get latest analysis
        latest_analysis = max(analyses, key=lambda a: a.created_at)
        
        result = {
            'total_analyses': total_analyses,
            'significant_analyses': significant_analyses,
            'significance_rate': significant_analyses / total_analyses if total_analyses > 0 else 0,
            'test_type_counts': test_type_counts,
            'latest_analysis': latest_analysis.to_dict() if latest_analysis else None
        }
        print(result)
        return result