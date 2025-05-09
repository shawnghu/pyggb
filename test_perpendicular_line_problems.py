import unittest
import numpy as np

from perpendicular_line_problems import count_intersections, create_problem

class TestPolygonDiagonals(unittest.TestCase):
    
    def test_count_intersections_no_diagonals(self):
        """Test with empty diagonals list."""
        vertices = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # Square
        diagonals = []
        self.assertEqual(count_intersections(diagonals, vertices), 0)
    
    def test_count_intersections_square(self):
        """Test with known case: square with both diagonals."""
        vertices = [(1, 1), (-1, 1), (-1, -1), (1, -1)]  # Square
        diagonals = [(0, 2), (1, 3)]  # Both diagonals
        self.assertEqual(count_intersections(diagonals, vertices), 1)  # Intersect at center
    
    def test_count_intersections_pentagon(self):
        """Test with a regular pentagon and selected diagonals."""
        # Create a regular pentagon
        angles = np.linspace(0, 2*np.pi, 6)[:-1]
        vertices = [(np.cos(angle), np.sin(angle)) for angle in angles]
        
        # Diagonals (0,2) and (1,3) should intersect in a pentagon
        diagonals = [(0, 2), (1, 3)]
        self.assertEqual(count_intersections(diagonals, vertices), 0)
        
        # Adding diagonal (2,4) creates more intersections
        diagonals = [(0, 2), (1, 3), (2, 4)]
        self.assertEqual(count_intersections(diagonals, vertices), 0)
    
    def test_count_intersections_hexagon(self):
        """Test with a regular hexagon and selected diagonals."""
        # Create a regular hexagon
        angles = np.linspace(0, 2*np.pi, 7)[:-1]
        vertices = [(np.cos(angle), np.sin(angle)) for angle in angles]
        
        diagonals = [(0, 4), (2, 5)]
        self.assertEqual(count_intersections(diagonals, vertices), 1)
        
        # Adding diagonal (2,4) creates more intersections
        diagonals = [(0, 4), (2, 5), (1, 3)]
        self.assertEqual(count_intersections(diagonals, vertices), 2)
    
    def test_count_intersections_12gon(self):
        """Test with a regular 12gon and selected diagonals."""
        # Create a regular 12gon
        angles = np.linspace(0, 2*np.pi, 13)[:-1]
        vertices = [(np.cos(angle), np.sin(angle)) for angle in angles]
        
        diagonals = [(0, 5), (6, 11), (2, 9)]
        self.assertEqual(count_intersections(diagonals, vertices), 2)
        
        diagonals = [(0, 5), (6, 11), (2, 9), (3, 8)]
        self.assertEqual(count_intersections(diagonals, vertices), 4)

    def test_count_intersections_8gon(self):
        """Test with a regular 8gon and selected diagonals."""
        # Create a regular 8gon
        angles = np.linspace(0, 2*np.pi, 9)[:-1]
        vertices = [(np.cos(angle), np.sin(angle)) for angle in angles]
        
        diagonals = [(6, 4), (1, 7), (5, 0), (4, 1), (4, 0), (2, 5), (6, 3), (5, 3), (1, 3), (5, 7), (5, 1), (2, 0), (4, 2), (4, 7)]
        self.assertEqual(count_intersections(diagonals, vertices), 13)
    

if __name__ == '__main__':
    unittest.main()