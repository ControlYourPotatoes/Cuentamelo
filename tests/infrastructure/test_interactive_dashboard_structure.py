import pytest
from pathlib import Path
import re
from bs4 import BeautifulSoup


class TestInteractiveDashboardStructure:
    """Test suite for interactive dashboard HTML structure and CSS layout"""
    
    @pytest.fixture
    def dashboard_path(self):
        return Path("dashboard/interactive.html")
    
    @pytest.fixture
    def css_path(self):
        return Path("dashboard/assets/interactive.css")
    
    @pytest.fixture
    def js_path(self):
        return Path("dashboard/assets/interactive.js")
    
    def test_dashboard_file_exists(self, dashboard_path):
        """Test that the interactive dashboard HTML file exists"""
        assert dashboard_path.exists(), f"Dashboard file {dashboard_path} should exist"
    
    def test_css_file_exists(self, css_path):
        """Test that the interactive dashboard CSS file exists"""
        assert css_path.exists(), f"CSS file {css_path} should exist"
    
    def test_js_file_exists(self, js_path):
        """Test that the interactive dashboard JavaScript file exists"""
        assert js_path.exists(), f"JavaScript file {js_path} should exist"
    
    def test_html_structure_semantic(self, dashboard_path):
        """Test that HTML uses semantic elements"""
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for semantic HTML elements
        assert soup.find('header'), "Should have a header element"
        assert soup.find('main'), "Should have a main element"
        assert soup.find('section'), "Should have section elements"
        
        # Check for proper document structure
        assert soup.find('html'), "Should have html root element"
        assert soup.find('head'), "Should have head element"
        assert soup.find('body'), "Should have body element"
    
    def test_html_meta_tags(self, dashboard_path):
        """Test that HTML has proper meta tags"""
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        head = soup.find('head')
        
        # Check for essential meta tags
        charset_meta = head.find('meta', charset=True)
        assert charset_meta, "Should have charset meta tag"
        assert charset_meta['charset'].lower() == 'utf-8', "Should use UTF-8 charset"
        
        viewport_meta = head.find('meta', attrs={'name': 'viewport'})
        assert viewport_meta, "Should have viewport meta tag"
        assert 'width=device-width' in viewport_meta.get('content', ''), "Should have responsive viewport"
    
    def test_css_grid_layout(self, css_path):
        """Test that CSS uses Grid layout for main structure"""
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for CSS Grid usage
        grid_patterns = [
            r'display:\s*grid',
            r'grid-template-columns',
            r'grid-template-rows',
            r'grid-area'
        ]
        
        for pattern in grid_patterns:
            assert re.search(pattern, css_content, re.IGNORECASE), f"Should use CSS Grid: {pattern}"
    
    def test_css_responsive_design(self, css_path):
        """Test that CSS includes responsive design breakpoints"""
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for media queries for responsive design
        media_query_pattern = r'@media\s+\(.*\)'
        assert re.search(media_query_pattern, css_content), "Should include media queries for responsive design"
    
    def test_css_professional_styling(self, css_path):
        """Test that CSS includes professional styling elements"""
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for professional styling patterns
        professional_patterns = [
            r'border-radius',  # Rounded corners
            r'box-shadow',     # Shadows for depth
            r'transition',     # Smooth transitions
            r'gradient',       # Modern gradients
        ]
        
        for pattern in professional_patterns:
            assert re.search(pattern, css_content, re.IGNORECASE), f"Should include professional styling: {pattern}"
    
    def test_js_modular_architecture(self, js_path):
        """Test that JavaScript follows modular architecture"""
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for modular patterns
        modular_patterns = [
            r'class\s+\w+',           # Class definitions
            r'addEventListener',       # Event handling
            r'export',                 # Module exports (if using modules)
            r'import',                 # Module imports (if using modules)
        ]
        
        # At least some modular patterns should be present
        found_patterns = sum(1 for pattern in modular_patterns if re.search(pattern, js_content))
        assert found_patterns >= 2, "Should follow modular JavaScript architecture"
    
    def test_component_separation(self):
        """Test that components are separated into different files"""
        component_files = [
            "dashboard/components/news-selector.js",
            "dashboard/components/character-selector.js", 
            "dashboard/components/results-display.js",
            "dashboard/components/sse-handler.js"
        ]
        
        for component_file in component_files:
            component_path = Path(component_file)
            assert component_path.exists(), f"Component file {component_file} should exist"
    
    def test_assets_directory_structure(self):
        """Test that assets directory has proper structure"""
        assets_dir = Path("dashboard/assets")
        assert assets_dir.exists(), "Assets directory should exist"
        assert assets_dir.is_dir(), "Assets should be a directory"
        
        # Check for expected files
        expected_files = [
            "interactive.css",
            "interactive.js"
        ]
        
        for file_name in expected_files:
            file_path = assets_dir / file_name
            assert file_path.exists(), f"Asset file {file_name} should exist"
    
    def test_html_accessibility(self, dashboard_path):
        """Test that HTML includes accessibility features"""
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for accessibility attributes
        form_elements = soup.find_all(['input', 'select', 'textarea', 'button'])
        for element in form_elements:
            if element.name in ['input', 'select', 'textarea']:
                # Form elements should have labels or aria-labels
                has_label = element.find_previous('label') or element.get('aria-label') or element.get('id')
                assert has_label, f"Form element {element.name} should have label or aria-label"
        
        # Check for semantic landmarks
        landmarks = soup.find_all(['header', 'main', 'nav', 'section', 'article', 'aside', 'footer'])
        assert len(landmarks) >= 3, "Should have multiple semantic landmarks for accessibility" 