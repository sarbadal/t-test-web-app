"""Validation utilities for data and parameters."""

import json
from typing import Dict, Any, Tuple, Union


def validate_json_data(data: Union[str, Dict[str, Any]]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate JSON data for t-test analysis.
    
    Returns:
        Tuple of (is_valid, error_message, parsed_data)
    """
    # Parse JSON if it's a string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}", {}
    
    if not isinstance(data, dict):
        return False, "Data must be a JSON object", {}
    
    # Check for valid data structures
    valid_structures = [
        'data' in data,  # One-sample
        'before' in data and 'after' in data,  # Paired
        'group1' in data and 'group2' in data,  # Two-sample
    ]
    
    if not any(valid_structures):
        return False, (
            "Invalid data structure. Must contain 'data', 'before'/'after', or 'group1'/'group2'"
        ), {}
    
    # Validate specific data types and constraints
    try:
        if 'data' in data:
            return _validate_one_sample_data(data)
        elif 'before' in data and 'after' in data:
            return _validate_paired_data(data)
        elif 'group1' in data and 'group2' in data:
            return _validate_two_sample_data(data)
    except Exception as e:
        return False, f"Data validation error: {str(e)}", {}
    
    return True, "", data


def _validate_one_sample_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate one-sample t-test data."""
    sample_data = data['data']
    
    if not isinstance(sample_data, list):
        return False, "One-sample data must be a list of numbers", {}
    
    if len(sample_data) == 0:
        return False, "One-sample data cannot be empty", {}
    
    if len(sample_data) < 2:
        return False, "One-sample data must contain at least 2 values", {}
    
    # Check if all values are numeric
    for i, value in enumerate(sample_data):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Value at index {i} is not numeric: {value}", {}
        if not (-1e10 <= value <= 1e10):  # Reasonable bounds
            return False, f"Value at index {i} is out of reasonable range: {value}", {}
    
    return True, "", data


def _validate_paired_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate paired t-test data."""
    before_data = data['before']
    after_data = data['after']
    
    if not isinstance(before_data, list) or not isinstance(after_data, list):
        return False, "Paired data must be lists of numbers", {}
    
    if len(before_data) == 0 or len(after_data) == 0:
        return False, "Paired data cannot be empty", {}
    
    if len(before_data) != len(after_data):
        return False, "Paired data must have equal lengths", {}
    
    if len(before_data) < 2:
        return False, "Paired data must contain at least 2 pairs", {}
    
    # Check if all values are numeric
    for i, (before_val, after_val) in enumerate(zip(before_data, after_data)):
        if not isinstance(before_val, (int, float)) or isinstance(before_val, bool):
            return False, f"Before value at index {i} is not numeric: {before_val}", {}
        if not isinstance(after_val, (int, float)) or isinstance(after_val, bool):
            return False, f"After value at index {i} is not numeric: {after_val}", {}
        if not (-1e10 <= before_val <= 1e10):
            return False, f"Before value at index {i} is out of reasonable range: {before_val}", {}
        if not (-1e10 <= after_val <= 1e10):
            return False, f"After value at index {i} is out of reasonable range: {after_val}", {}
    
    return True, "", data


def _validate_two_sample_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate two-sample t-test data."""
    group1_data = data['group1']
    group2_data = data['group2']
    
    if not isinstance(group1_data, list) or not isinstance(group2_data, list):
        return False, "Two-sample data must be lists of numbers", {}
    
    if len(group1_data) == 0 or len(group2_data) == 0:
        return False, "Two-sample groups cannot be empty", {}
    
    if len(group1_data) < 2 or len(group2_data) < 2:
        return False, "Each group must contain at least 2 values", {}
    
    # Check if all values are numeric
    for i, value in enumerate(group1_data):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Group1 value at index {i} is not numeric: {value}", {}
        if not (-1e10 <= value <= 1e10):
            return False, f"Group1 value at index {i} is out of reasonable range: {value}", {}
    
    for i, value in enumerate(group2_data):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Group2 value at index {i} is not numeric: {value}", {}
        if not (-1e10 <= value <= 1e10):
            return False, f"Group2 value at index {i} is out of reasonable range: {value}", {}
    
    return True, "", data


def validate_confidence_level(confidence: Union[str, float]) -> Tuple[bool, str, float]:
    """
    Validate confidence level parameter.
    
    Returns:
        Tuple of (is_valid, error_message, parsed_confidence)
    """
    try:
        confidence_level = float(confidence)
    except (ValueError, TypeError):
        return False, "Confidence level must be a number", 0.0
    
    if not (0 < confidence_level < 1):
        return False, "Confidence level must be between 0 and 1 (exclusive)", 0.0
    
    # Common confidence levels
    common_levels = [0.90, 0.95, 0.99, 0.999]
    if confidence_level not in common_levels:
        # Allow any reasonable confidence level, but warn about uncommon ones
        if confidence_level < 0.5 or confidence_level > 0.9999:
            return False, "Confidence level should typically be between 0.5 and 0.9999", 0.0
    
    return True, "", confidence_level


def validate_dataset_name(name: str) -> Tuple[bool, str, str]:
    """
    Validate dataset name.
    
    Returns:
        Tuple of (is_valid, error_message, cleaned_name)
    """
    if not isinstance(name, str):
        return False, "Dataset name must be a string", ""
    
    # Clean the name
    cleaned_name = name.strip()
    
    if not cleaned_name:
        return False, "Dataset name cannot be empty", ""
    
    if len(cleaned_name) > 200:
        return False, "Dataset name cannot exceed 200 characters", ""
    
    # Check for invalid characters (basic validation)
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        if char in cleaned_name:
            return False, f"Dataset name cannot contain '{char}'", ""
    
    return True, "", cleaned_name


def validate_file_upload(file) -> Tuple[bool, str]:
    """
    Validate uploaded file.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file uploaded"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    if not file.filename.lower().endswith('.json'):
        return False, "File must be a JSON file (.json)"
    
    # Check file size (10MB limit)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        return False, f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
    
    return True, ""