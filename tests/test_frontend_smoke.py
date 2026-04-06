cat > tests/test_frontend_smoke.py << 'EOF'
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFrontendFilesExist(unittest.TestCase):
    
    def setUp(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.frontend_path = os.path.join(self.base_path, 'frontend')
        self.components_path = os.path.join(self.frontend_path, 'components')
        
    def test_frontend_directory_exists(self):
        self.assertTrue(os.path.exists(self.frontend_path))
        
    def test_index_html_exists(self):
        path = os.path.join(self.frontend_path, 'index.html')
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        
    def test_styles_css_exists(self):
        path = os.path.join(self.frontend_path, 'styles.css')
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        
    def test_script_js_exists(self):
        path = os.path.join(self.frontend_path, 'script.js')
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        
    def test_app_py_exists(self):
        path = os.path.join(self.frontend_path, 'app.py')
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        
    def test_components_directory_exists(self):
        self.assertTrue(os.path.exists(self.components_path))
        
    def test_component_files_exist(self):
        components = ['header.html', 'incident_summary.html', 'service_cards.html',
                      'logs_panel.html', 'metrics_panel.html', 'action_panel.html']
        for comp in components:
            path = os.path.join(self.components_path, comp)
            self.assertTrue(os.path.exists(path), f"Missing {comp}")


class TestHTMLStructure(unittest.TestCase):
    
    def setUp(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.index_path = os.path.join(self.base_path, 'frontend', 'index.html')
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
            
    def test_html_has_doctype(self):
        self.assertIn('<!DOCTYPE html>', self.html_content.upper())
        
    def test_html_has_title(self):
        self.assertIn('<title>', self.html_content)
        
    def test_html_has_body(self):
        self.assertIn('<body>', self.html_content)
        
    def test_html_has_header(self):
        self.assertIn('class="header"', self.html_content)
        
    def test_html_has_container(self):
        self.assertIn('class="container"', self.html_content)
        
    def test_html_has_action_buttons(self):
        self.assertIn('id="initBtn"', self.html_content)
        self.assertIn('id="resetBtn"', self.html_content)
        self.assertIn('id="actionBtn"', self.html_content)


class TestCSSStructure(unittest.TestCase):
    
    def setUp(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.css_path = os.path.join(self.base_path, 'frontend', 'styles.css')
        with open(self.css_path, 'r', encoding='utf-8') as f:
            self.css_content = f.read()
            
    def test_css_has_body_styles(self):
        self.assertIn('body', self.css_content)
        
    def test_css_has_header_styles(self):
        self.assertIn('.header', self.css_content)
        
    def test_css_has_container_styles(self):
        self.assertIn('.container', self.css_content)
        
    def test_css_has_button_styles(self):
        self.assertIn('.btn', self.css_content)
        
    def test_css_no_shell_artifacts(self):
        self.assertNotIn('cat >', self.css_content)
        self.assertNotIn('<< EOF', self.css_content)


if __name__ == '__main__':
    unittest.main()
EOF