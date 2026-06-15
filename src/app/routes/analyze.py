import json
from datetime import datetime
from flask import Blueprint, jsonify, request, session, current_app

from ..services import AnalysisService, DataSetService, UserService
from ..utils.validators import validate_json_data, validate_confidence_level, validate_file_upload, validate_dataset_name
from ..utils.decorators import api_login_required

bp = Blueprint('analyze', __name__)

@bp.route('/analyze', methods=['POST'])
@api_login_required
def analyze_data() -> jsonify:
    """Analyze uploaded data with t-test and store results in database."""
    try:
        # Get current user
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not found in session'}), 401
        
        # Validate file upload
        file = request.files.get('file')
        is_valid_file, file_error = validate_file_upload(file)
        if not is_valid_file:
            return jsonify({'error': file_error}), 400
        
        # Validate confidence level
        confidence_input = request.form.get('confidence', '0.95')
        is_valid_confidence, confidence_error, confidence_level = validate_confidence_level(confidence_input)
        if not is_valid_confidence:
            return jsonify({'error': confidence_error}), 400
        
        # Read and validate JSON data
        try:
            raw_data = json.load(file)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON file: {str(e)}'}), 400
        
        is_valid_data, data_error, data = validate_json_data(raw_data)
        if not is_valid_data:
            return jsonify({'error': data_error}), 400
        
        # Generate dataset name from filename or use default
        dataset_name = request.form.get('dataset_name') or file.filename
        is_valid_name, name_error, dataset_name = validate_dataset_name(dataset_name)
        if not is_valid_name:
            return jsonify({'error': name_error}), 400
        
        # Create dataset
        dataset = DataSetService.create_dataset(
            name=dataset_name,
            data=data,
            original_filename=file.filename,
            user_id=user_id,
            description=request.form.get('description', 'Uploaded via web interface')
        )
        
        # Create analysis
        analysis_name = request.form.get('analysis_name', f'Analysis of {dataset_name}')
        analysis = AnalysisService.create_analysis(
            data=data,
            confidence_level=confidence_level,
            user_id=user_id,
            dataset_id=dataset.id,
            name=analysis_name
        )
        
        # Store latest analysis ID in session for backward compatibility
        session['latest_analysis_id'] = analysis.id
        
        # Return analysis results
        result = analysis.to_dict()
        current_app.logger.info(f"Analysis completed successfully for user {user_id}")
        
        return jsonify(result)
        
    except ValueError as e:
        current_app.logger.warning(f"Validation error in analysis: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in analysis: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@bp.route('/api/ttest-result', methods=['GET'])
@api_login_required
def get_ttest_result() -> jsonify:
    """API endpoint to retrieve the latest t-test results in JSON format"""
    user_id = session.get('user_id')
    
    # Check if there's a latest analysis ID in session
    latest_analysis_id = session.get('latest_analysis_id')
    
    if not latest_analysis_id:
        return jsonify({'error': 'No t-test results available. Please run an analysis first.'}), 404
    
    # Get the analysis from database
    analysis = AnalysisService.get_analysis_by_id(latest_analysis_id, user_id)
    
    if not analysis:
        return jsonify({'error': 'Analysis not found or access denied'}), 404
    
    # Get the associated dataset
    dataset = DataSetService.get_dataset_by_id(analysis.dataset_id, user_id)
    
    return jsonify({
        'status': 'success',
        'data': {
            'analysis_result': analysis.to_dict(include_raw=True),
            'dataset_info': dataset.to_dict(include_data=True) if dataset else None,
            'timestamp': analysis.created_at.isoformat()
        }
    })


@bp.route('/api/analyses', methods=['GET'])
@api_login_required
def get_user_analyses() -> jsonify:
    """API endpoint to retrieve user's analysis history"""
    user_id = session.get('user_id')
    
    # Get pagination parameters
    limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 results
    
    # Get analyses
    analyses = AnalysisService.get_user_analyses(user_id, limit)
    
    return jsonify({
        'status': 'success',
        'data': {
            'analyses': [analysis.to_dict() for analysis in analyses],
            'count': len(analyses)
        }
    })


@bp.route('/api/analyses/<int:analysis_id>', methods=['GET'])
@api_login_required
def get_analysis_by_id(analysis_id: int) -> jsonify:
    """API endpoint to retrieve a specific analysis"""
    user_id = session.get('user_id')
    
    analysis = AnalysisService.get_analysis_by_id(analysis_id, user_id)
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify({
        'status': 'success',
        'data': analysis.to_dict(include_raw=True)
    })


@bp.route('/api/analyses/<int:analysis_id>', methods=['DELETE'])
@api_login_required
def delete_analysis(analysis_id: int) -> jsonify:
    """API endpoint to delete an analysis"""
    user_id = session.get('user_id')
    
    success = AnalysisService.delete_analysis(analysis_id, user_id)
    
    if not success:
        return jsonify({'error': 'Analysis not found or cannot be deleted'}), 404
    
    return jsonify({
        'status': 'success',
        'message': 'Analysis deleted successfully'
    })


@bp.route('/api/datasets', methods=['GET'])
@api_login_required
def get_user_datasets() -> jsonify:
    """API endpoint to retrieve user's datasets"""
    user_id = session.get('user_id')
    
    # Get pagination parameters
    limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 results
    
    # Get datasets
    datasets = DataSetService.get_user_datasets(user_id, limit)
    
    return jsonify({
        'status': 'success',
        'data': {
            'datasets': [dataset.to_dict() for dataset in datasets],
            'count': len(datasets)
        }
    })


@bp.route('/api/summary', methods=['GET'])
@api_login_required
def get_user_summary() -> jsonify:
    """API endpoint to get user's analysis and dataset summary"""
    user_id = session.get('user_id')
    
    # Get summaries
    analysis_summary = AnalysisService.get_analysis_summary(user_id)
    dataset_summary = DataSetService.get_dataset_summary(user_id)
    
    return jsonify({
        'status': 'success',
        'data': {
            'analysis_summary': analysis_summary,
            'dataset_summary': dataset_summary
        }
    })