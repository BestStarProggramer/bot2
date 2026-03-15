import pytest
from services.queue_service import calculate_new_weight
from config import K_FACTOR

class TestWeightCalculation:
    
    def test_weight_decreases_for_first_positions(self):
        current_weight = 1.0
        position = 1
        total_n = 10
        new_weight = calculate_new_weight(current_weight, position, total_n)
        assert new_weight < current_weight
        assert new_weight >= 0.1
    
    def test_weight_increases_for_last_positions(self):
        current_weight = 1.0
        position = 10
        total_n = 10
        new_weight = calculate_new_weight(current_weight, position, total_n)
        assert new_weight > current_weight
        assert new_weight <= 10.0
    
    def test_weight_unchanged_for_single_person(self):
        current_weight = 1.0
        position = 1
        total_n = 1
        new_weight = calculate_new_weight(current_weight, position, total_n)
        assert new_weight == current_weight
    
    def test_weight_clamped_to_minimum(self):
        current_weight = 0.01
        position = 1
        total_n = 100
        new_weight = calculate_new_weight(current_weight, position, total_n)
        assert new_weight >= 0.1
    
    def test_weight_clamped_to_maximum(self):
        current_weight = 100.0
        position = 100
        total_n = 100
        new_weight = calculate_new_weight(current_weight, position, total_n)
        assert new_weight <= 10.0
    
    def test_middle_position_unchanged(self):
        current_weight = 1.0
        position = 5
        total_n = 10
        new_weight = calculate_new_weight(current_weight, position, total_n)
        assert abs(new_weight - current_weight) < 0.1