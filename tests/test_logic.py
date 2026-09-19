from snake_game.logic import (
    advance_snake,
    compute_speed,
    has_self_collision,
    has_wall_collision,
    is_opposite_direction,
    next_head_position,
    random_food_position,
)


def test_next_head_position_moves_one_step_in_each_direction():
    assert next_head_position((100, 100), "Right", 20) == (120, 100)
    assert next_head_position((100, 100), "Left", 20) == (80, 100)
    assert next_head_position((100, 100), "Up", 20) == (100, 80)
    assert next_head_position((100, 100), "Down", 20) == (100, 120)


def test_is_opposite_direction():
    assert is_opposite_direction("Up", "Down") is True
    assert is_opposite_direction("Down", "Up") is True
    assert is_opposite_direction("Left", "Right") is True
    assert is_opposite_direction("Up", "Left") is False
    assert is_opposite_direction("Right", "Right") is False


def test_advance_snake_without_growth_keeps_length_and_drops_tail():
    body = [(100, 100), (80, 100), (60, 100)]
    result = advance_snake(body, "Right", 20, grow=False)
    assert result == [(120, 100), (100, 100), (80, 100)]
    assert len(result) == len(body)


def test_advance_snake_with_growth_adds_one_segment():
    body = [(100, 100), (80, 100), (60, 100)]
    result = advance_snake(body, "Right", 20, grow=True)
    assert result == [(120, 100), (100, 100), (80, 100), (60, 100)]
    assert len(result) == len(body) + 1


def test_has_wall_collision_true_on_boundary_edges():
    assert has_wall_collision((0, 100), wall_x=(0, 600), wall_y=(20, 620)) is True
    assert has_wall_collision((600, 100), wall_x=(0, 600), wall_y=(20, 620)) is True
    assert has_wall_collision((100, 20), wall_x=(0, 600), wall_y=(20, 620)) is True
    assert has_wall_collision((100, 620), wall_x=(0, 600), wall_y=(20, 620)) is True


def test_has_wall_collision_false_inside_bounds():
    assert has_wall_collision((100, 100), wall_x=(0, 600), wall_y=(20, 620)) is False


def test_has_self_collision():
    body = [(80, 100), (60, 100)]
    assert has_self_collision((80, 100), body) is True
    assert has_self_collision((999, 999), body) is False


def test_random_food_position_avoids_occupied_cells():
    occupied = [(20, 60), (20, 80)]
    # A deterministic fake rng that always returns the first occupied cell
    # for the first two calls, then a free one.
    calls = iter([1, 3, 1, 3, 2, 4])

    def fake_rng(_low, _high):
        return next(calls)

    position = random_food_position(occupied, (1, 5), (3, 6), step=20, rng=fake_rng)
    assert position not in occupied
    assert position == (40, 80)


def test_compute_speed_increases_every_n_points():
    assert compute_speed(score=0, base_speed=15, step_every=5) == 15
    assert compute_speed(score=4, base_speed=15, step_every=5) == 15
    assert compute_speed(score=5, base_speed=15, step_every=5) == 16
    assert compute_speed(score=15, base_speed=15, step_every=5) == 18
