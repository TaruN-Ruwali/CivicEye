"""
CivicEye AI Detection Package

This package provides AI-powered detection capabilities for infrastructure issues
including garbage, potholes, and water leakage.

Main components:
- detector_manager: Orchestrates all detectors
- detectors: Individual detector modules
"""

from .detector_manager import run_all, run_all_for_api, build_normal_output

__all__ = ['run_all', 'run_all_for_api', 'build_normal_output']

