import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
import sys
from main import WindowSelector, FloatingInput

class TestApplicationFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
    
    def test_window_selection_flow(self):
        """Test the complete window selection flow"""
        # Create window selector
        selector = WindowSelector()
        
        # Wait for window list to populate
        QTimer.singleShot(100, lambda: self.process_selector(selector))
        
        # Show selector and start event loop
        selector.show()
        QTimer.singleShot(2000, self.app.quit)  # Quit after 2 seconds
        self.app.exec()
    
    def process_selector(self, selector):
        """Process the window selector"""
        # Verify window list is populated
        self.assertGreater(selector.window_list.count(), 0)
        
        # Select first window
        selector.window_list.setCurrentRow(0)
        
        # Click select button
        selector.select_button.click()
        
        # Add delay before verification
        QTimer.singleShot(200, lambda: self.verify_selection(selector))
    
    def verify_selection(self, selector):
        """Verify the window selection was successful"""
        # Verify floating input was created
        floating_inputs = [w for w in self.app.topLevelWidgets() if isinstance(w, FloatingInput)]
        self.assertEqual(len(floating_inputs), 1)
        
        floating_input = floating_inputs[0]
        
        # Verify floating input state
        self.assertIsNotNone(floating_input.target_window)
        self.assertIsNotNone(floating_input.target_name)
        self.assertTrue(floating_input.isVisible())
        self.assertTrue(floating_input.highlight.isVisible())
    
    def test_reselection_flow(self):
        """Test the window reselection flow"""
        # Create initial floating input
        input_window = FloatingInput()
        input_window.show()
        
        # Click reselect button
        QTimer.singleShot(100, lambda: self.process_reselection(input_window))
        
        # Start event loop
        QTimer.singleShot(1000, self.app.quit)  # Quit after 1 second
        self.app.exec()
    
    def process_reselection(self, input_window):
        """Process the window reselection"""
        # Store initial target
        initial_target = input_window.target_window
        
        # Click reselect button (simulated)
        input_window.reselect_window()
        
        # Find selector window
        selectors = [w for w in self.app.topLevelWidgets() if isinstance(w, WindowSelector)]
        self.assertEqual(len(selectors), 1)
        
        selector = selectors[0]
        
        # Select a different window (first one)
        selector.window_list.setCurrentRow(0)
        selector.select_button.click()
        
        # Add a small delay to ensure highlight is updated
        QTimer.singleShot(200, lambda: self.verify_reselection(input_window, initial_target))
    
    def verify_reselection(self, input_window, initial_target):
        """Verify the reselection was successful"""
        # Verify target was updated
        self.assertNotEqual(input_window.target_window, initial_target)
        self.assertTrue(input_window.highlight.isVisible())

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests() 