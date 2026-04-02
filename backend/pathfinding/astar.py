import numpy as np
from skimage.graph import route_through_array  # type: ignore


def find_path(
    cost_array: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """
    Find the minimum-cost path through the cost array using A*.
    start and end are (row, col) indices.
    Returns list of (row, col) tuples.
    """
    # Ensure start/end are within bounds
    n_rows, n_cols = cost_array.shape
    start = (
        int(np.clip(start[0], 0, n_rows - 1)),
        int(np.clip(start[1], 0, n_cols - 1)),
    )
    end = (
        int(np.clip(end[0], 0, n_rows - 1)),
        int(np.clip(end[1], 0, n_cols - 1)),
    )

    if start == end:
        return [start]

    try:
        path_indices, _ = route_through_array(
            cost_array,
            start=start,
            end=end,
            fully_connected=True,  # allow diagonal moves
            geometric=True,        # scale cost by distance (avoids diagonal bias)
        )
        return [(int(r), int(c)) for r, c in path_indices]
    except Exception as e:
        # Fallback: straight line of indices
        print(f"[astar] pathfinding failed: {e}, falling back to straight line")
        return [start, end]
