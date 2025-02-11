import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRect
import sys
from main import (
    WindowSelector, 
    FloatingInput, 
    WindowHighlight, 
    get_window_list,
    get_window_bounds,
    get_screen_for_window
)

class TestWindowManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance for tests
        cls.app = QApplication(sys.argv)
    
    def test_window_list_format(self):
        """Test that window list returns properly formatted data"""
        windows = get_window_list()
        self.assertIsInstance(windows, list)
        if windows:  # If any windows are found
            first_window = windows[0]
            self.assertIsInstance(first_window, tuple)
            self.assertEqual(len(first_window), 2)
            self.assertIsInstance(first_window[0], str)  # Window name
            self.assertIsInstance(first_window[1], int)  # Window ID
    
    def test_window_bounds(self):
        """Test window bounds calculation"""
        windows = get_window_list()
        if windows:
            window_id = windows[0][1]
            bounds = get_window_bounds(window_id)
            self.assertIsInstance(bounds, QRect)
            self.assertGreaterEqual(bounds.width(), 0)
            self.assertGreaterEqual(bounds.height(), 0)
    
    def test_window_selector_creation(self):
        """Test WindowSelector initialization"""
        selector = WindowSelector()
        self.assertIsNotNone(selector.window_list)
        self.assertIsNotNone(selector.select_button)
        self.assertEqual(selector.windowTitle(), "Select Window")
    
    def test_floating_input_creation(self):
        """Test FloatingInput initialization"""
        input_window = FloatingInput()
        self.assertIsNotNone(input_window.input_field)
        self.assertIsNotNone(input_window.highlight)
        self.assertIsNone(input_window.target_window)
        self.assertTrue(input_window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
    
    def test_window_highlight_creation(self):
        """Test WindowHighlight initialization"""
        highlight = WindowHighlight()
        self.assertTrue(highlight.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertTrue(highlight.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
    
    def test_floating_input_target_setting(self):
        """Test setting target window in FloatingInput"""
        input_window = FloatingInput()
        test_id = 12345
        test_name = "Test Window"
        input_window.set_target(test_id, test_name)
        self.assertEqual(input_window.target_window, test_id)
        self.assertEqual(input_window.target_name, test_name)
        self.assertEqual(input_window.window_title.text(), test_name)

class TestWindowHighlightBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
    
    def test_highlight_animation(self):
        """Test highlight animation timer"""
        highlight = WindowHighlight()
        self.assertTrue(highlight.animation_timer.isActive())
        self.assertEqual(highlight.animation_timer.interval(), 1000)
    
    def test_highlight_cleanup(self):
        """Test proper cleanup of highlight resources"""
        highlight = WindowHighlight()
        self.assertTrue(highlight.animation_timer.isActive())
        highlight.close()
        self.assertFalse(highlight.animation_timer.isActive())

class TestFloatingInputBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
    
    def test_auto_type_timer(self):
        """Test auto-type timer initialization"""
        input_window = FloatingInput()
        self.assertTrue(input_window.type_timer.isActive())
        self.assertEqual(input_window.type_timer.interval(), 3000)
    
    def test_highlight_update_timer(self):
        """Test highlight update timer"""
        input_window = FloatingInput()
        self.assertTrue(input_window.highlight_timer.isActive())
        self.assertEqual(input_window.highlight_timer.interval(), 100)
    
    def test_cleanup(self):
        """Test proper cleanup of timers and resources"""
        input_window = FloatingInput()
        self.assertTrue(input_window.type_timer.isActive())
        self.assertTrue(input_window.highlight_timer.isActive())
        input_window.close()
        self.assertFalse(input_window.type_timer.isActive())
        self.assertFalse(input_window.highlight_timer.isActive())

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests() 