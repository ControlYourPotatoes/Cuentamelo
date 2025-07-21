#!/usr/bin/env python3
"""
Comprehensive test runner for Cuentamelo testing framework revamp.

This script implements the testing framework revamp plan with:
- pytest-based test execution
- Comprehensive coverage reporting
- Parallel test execution
- Test categorization and filtering
- Integration with CI/CD pipeline
- Performance monitoring
"""

import sys
import os
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pytest


class TestRunner:
    """Comprehensive test runner for the Cuentamelo project."""
    
    def __init__(self, project_root: str = None):
        """Initialize test runner."""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.coverage_dir = self.project_root / "coverage"
        self.results_dir = self.project_root / "test_results"
        
        # Ensure directories exist
        self.coverage_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Check for pytest configuration
        self.pytest_config = self.project_root / "pytest_revamp.ini"
        if not self.pytest_config.exists():
            self.pytest_config = self.project_root / "pytest.ini"
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check if required testing dependencies are available."""
        dependencies = {
            "pytest": False,
            "pytest_cov": False,
            "pytest_xdist": False
        }
        
        try:
            import pytest
            dependencies["pytest"] = True
        except ImportError:
            pass
        
        try:
            import pytest_cov
            dependencies["pytest_cov"] = True
        except ImportError:
            pass
        
        try:
            import pytest_xdist
            dependencies["pytest_xdist"] = True
        except ImportError:
            pass
        
        return dependencies
    
    def run_unit_tests(self, parallel: bool = True, coverage: bool = True) -> Dict[str, Any]:
        """Run unit tests with optional parallel execution and coverage."""
        print("🧪 Running unit tests...")
        
        dependencies = self._check_dependencies()
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "unit"),
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--durations=10"
        ]
        
        # Add pytest config if available
        if self.pytest_config.exists():
            cmd.extend(["-c", str(self.pytest_config)])
        
        if parallel and dependencies["pytest_xdist"]:
            cmd.extend(["-n", "auto"])
        
        if coverage and dependencies["pytest_cov"]:
            cmd.extend([
                "--cov=app",
                "--cov-report=html:" + str(self.coverage_dir / "html"),
                "--cov-report=xml:" + str(self.coverage_dir / "coverage.xml"),
                "--cov-report=term-missing"
            ])
        
        # Add unit test markers
        cmd.extend(["-m", "unit"])
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            "type": "unit",
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    def run_integration_tests(self, coverage: bool = False) -> Dict[str, Any]:
        """Run integration tests."""
        print("🔗 Running integration tests...")
        
        dependencies = self._check_dependencies()
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "integration"),
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--durations=10"
        ]
        
        # Add pytest config if available
        if self.pytest_config.exists():
            cmd.extend(["-c", str(self.pytest_config)])
        
        if coverage and dependencies["pytest_cov"]:
            cmd.extend([
                "--cov=app",
                "--cov-report=html:" + str(self.coverage_dir / "integration_html"),
                "--cov-report=xml:" + str(self.coverage_dir / "integration_coverage.xml")
            ])
        
        # Add integration test markers
        cmd.extend(["-m", "integration"])
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            "type": "integration",
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    def run_infrastructure_tests(self, coverage: bool = True) -> Dict[str, Any]:
        """Run infrastructure component tests."""
        print("🏗️ Running infrastructure tests...")
        
        dependencies = self._check_dependencies()
        
        infrastructure_tests = [
            "unit/services/test_command_broker_service.py",
            "unit/services/test_n8n_frontend_service.py", 
            "unit/services/test_frontend_event_bus.py",
            "unit/services/test_dependency_container.py"
        ]
        
        cmd = [
            "python", "-m", "pytest",
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--durations=10"
        ]
        
        # Add pytest config if available
        if self.pytest_config.exists():
            cmd.extend(["-c", str(self.pytest_config)])
        
        if coverage and dependencies["pytest_cov"]:
            cmd.extend([
                "--cov=app",
                "--cov-report=html:" + str(self.coverage_dir / "infrastructure_html"),
                "--cov-report=xml:" + str(self.coverage_dir / "infrastructure_coverage.xml")
            ])
        
        # Add infrastructure test files
        for test_file in infrastructure_tests:
            test_path = self.tests_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
            else:
                print(f"⚠️  Warning: Test file {test_file} not found")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            "type": "infrastructure",
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        print("⚡ Running performance tests...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "unit"),
            str(self.tests_dir / "integration"),
            str(self.tests_dir / "api"),
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--durations=10"
        ]
        
        # Add pytest config if available
        if self.pytest_config.exists():
            cmd.extend(["-c", str(self.pytest_config)])
        
        # Add performance test markers
        cmd.extend(["-m", "performance"])
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            "type": "performance",
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    def run_all_tests(self, parallel: bool = True, coverage: bool = True) -> Dict[str, Any]:
        """Run all test suites."""
        print("🚀 Running all test suites...")
        
        results = {}
        
        # Run different test categories
        results["unit"] = self.run_unit_tests(parallel=parallel, coverage=coverage)
        results["integration"] = self.run_integration_tests(coverage=coverage)
        results["infrastructure"] = self.run_infrastructure_tests(coverage=coverage)
        results["performance"] = self.run_performance_tests()
        
        # Calculate overall results
        all_success = all(result["success"] for result in results.values())
        total_duration = sum(result["duration"] for result in results.values())
        
        overall_result = {
            "type": "all",
            "success": all_success,
            "duration": total_duration,
            "results": results
        }
        
        return overall_result
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CURRENTAMELO TEST FRAMEWORK REVAMP - TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        if results["type"] == "all":
            # Overall summary
            report_lines.append("📊 OVERALL SUMMARY")
            report_lines.append("-" * 40)
            report_lines.append(f"Status: {'✅ PASSED' if results['success'] else '❌ FAILED'}")
            report_lines.append(f"Total Duration: {results['duration']:.2f} seconds")
            report_lines.append("")
            
            # Individual test suite results
            for test_type, result in results["results"].items():
                status = "✅ PASSED" if result["success"] else "❌ FAILED"
                report_lines.append(f"{test_type.upper()}: {status} ({result['duration']:.2f}s)")
            
            report_lines.append("")
            report_lines.append("📋 DETAILED RESULTS")
            report_lines.append("=" * 80)
            
            for test_type, result in results["results"].items():
                report_lines.append(f"\n{test_type.upper()} TESTS")
                report_lines.append("-" * 40)
                report_lines.append(f"Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
                report_lines.append(f"Duration: {result['duration']:.2f} seconds")
                
                if result["stdout"]:
                    report_lines.append("\nOutput:")
                    report_lines.append(result["stdout"][-1000:])  # Last 1000 chars
                
                if result["stderr"]:
                    report_lines.append("\nErrors:")
                    report_lines.append(result["stderr"])
        else:
            # Single test suite result
            status = "✅ PASSED" if results["success"] else "❌ FAILED"
            report_lines.append(f"Status: {status}")
            report_lines.append(f"Duration: {results['duration']:.2f} seconds")
            report_lines.append(f"Type: {results['type']}")
            
            if results["stdout"]:
                report_lines.append("\nOutput:")
                report_lines.append(results["stdout"])
            
            if results["stderr"]:
                report_lines.append("\nErrors:")
                report_lines.append(results["stderr"])
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("End of Test Report")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save test results to file."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        # Convert results to JSON-serializable format
        json_results = {
            "timestamp": time.time(),
            "type": results["type"],
            "success": results["success"],
            "duration": results["duration"],
            "return_code": results.get("return_code", 0)
        }
        
        if results["type"] == "all":
            json_results["results"] = {
                test_type: {
                    "success": result["success"],
                    "duration": result["duration"],
                    "return_code": result.get("return_code", 0)
                }
                for test_type, result in results["results"].items()
            }
        
        with open(filepath, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        return str(filepath)
    
    def run_with_coverage_analysis(self) -> Dict[str, Any]:
        """Run tests with comprehensive coverage analysis."""
        print("📊 Running tests with coverage analysis...")
        
        results = self.run_all_tests(parallel=False, coverage=True)
        
        # Generate coverage report
        coverage_report_path = self.coverage_dir / "coverage_summary.txt"
        with open(coverage_report_path, 'w') as f:
            f.write("Coverage Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Overall Success: {results['success']}\n")
            f.write(f"Total Duration: {results['duration']:.2f} seconds\n")
        
        return results


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Cuentamelo Test Framework Revamp Runner")
    parser.add_argument("--type", choices=["unit", "integration", "infrastructure", "performance", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage reports")
    parser.add_argument("--report", action="store_true", help="Generate detailed test report")
    parser.add_argument("--save-results", action="store_true", help="Save results to file")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner(project_root=args.project_root)
    
    # Check dependencies
    dependencies = runner._check_dependencies()
    print("🔍 Checking testing dependencies...")
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"   {dep}: {status}")
    
    if not dependencies["pytest"]:
        print("❌ pytest is not installed. Please install it with: pip install pytest")
        sys.exit(1)
    
    if not dependencies["pytest_cov"] and args.coverage:
        print("⚠️  pytest-cov is not installed. Coverage reporting will be disabled.")
        print("   Install with: pip install pytest-cov")
        args.coverage = False
    
    if not dependencies["pytest_xdist"] and args.parallel:
        print("⚠️  pytest-xdist is not installed. Parallel execution will be disabled.")
        print("   Install with: pip install pytest-xdist")
        args.parallel = False
    
    # Run tests based on type
    if args.type == "unit":
        results = runner.run_unit_tests(parallel=args.parallel, coverage=args.coverage)
    elif args.type == "integration":
        results = runner.run_integration_tests(coverage=args.coverage)
    elif args.type == "infrastructure":
        results = runner.run_infrastructure_tests(coverage=args.coverage)
    elif args.type == "performance":
        results = runner.run_performance_tests()
    else:  # all
        results = runner.run_all_tests(parallel=args.parallel, coverage=args.coverage)
    
    # Generate and display report
    if args.report:
        report = runner.generate_test_report(results)
        print(report)
    
    # Save results if requested
    if args.save_results:
        results_file = runner.save_test_results(results)
        print(f"Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main() 