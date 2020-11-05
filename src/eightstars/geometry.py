from __future__ import annotations

from itertools import chain
from math import cos, pi, sin
from typing import Optional


class Point:
    """A point in cartesian coordinates.
    """

    def __init__(self, x: float, y: float, decimals: int = 5) -> None:
        """Initializes Point, recording its coordinates with a precision
        rounded to given decimal places. The exact precision of coordinates
        is not so crucial, but leaving it as original numbers can lead
        to anomalies related to computer representation of floating-point
        numbers (eg. vertical straight could not be treated as such!).
        For full explanation read either:
            * https://docs.python.org/3/tutorial/floatingpoint.html
            * https://floating-point-gui.de/basic/
            * https://en.wikipedia.org/wiki/Floating-point_arithmetic

        Args:
            x (float): x-coordinate
            y (float): y-coordinate
            decimals (int): number of decimal places
        """
        self.x = round(x, decimals)
        self.y = round(y, decimals)

    def moved(self, x_distance: float = 0, y_distance: float = 0) -> Point:
        """Gives a new point shifted from the one in hand by  x and y distances.

        Args:
            x_distance (float, optional): Distance on x coordinate. Defaults to 0.
            y_distance (float, optional): Distance on y coordinate. Defaults to 0.

        Returns:
            Point: New point.
        """
        return Point(self.x + x_distance, self.y + y_distance)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class CoincidentStraights(Exception):
    pass


class Straight:
    """Straight line based on two points.
    """

    def __init__(self, A: Point, B: Point, decimals: int = 5) -> None:
        """Initializes Straight basing on coordinates of its two given
        points: A and B.
        Calculates slope (a) and x-intercept (b) of non-vertical straight
        (for linear equation), when A.x != B.x or accepts constant x for
        the opposite case. Results are rounded to given decimal places
        - see the explanation in Point class constructor.

        Args:
            A (Point): First point
            B (Point): Second point
            decimals (int): number of decimal places
        """
        if A.x != B.x:
            self.a = round((B.y - A.y) / (B.x - A.x), decimals)
            self.b = round(A.y - self.a * A.x, decimals)
            self.x = None
        else:
            self.x = A.x

    def intersection(self, other: Straight) -> Optional[Point]:
        """Calculates the point of intersection with other straight.

        Args:
            other (Straight): The other straight.

        Raises:
            CoincidentStraights: Exception raised when two straights are in
            coincidence.

        Returns:
            Optional[Point]: Point of intersection if the straights intersects
            or None if they are parallel.
        """
        if self.x is None and other.x is None:
            # None of the straight are vertical
            if self.a == other.a:
                if self.b == other.b:
                    # Coincidental non-vertical straights
                    raise CoincidentStraights
                else:
                    # Parallel non-vertical straights
                    return None
            else:
                # Non-parallel, non-vertical straights
                x = (other.b - self.b) / (self.a - other.a)
                y = self.a * x + self.b
        elif self.x is not None and other.x is not None:
            # Both straight vertical
            if self.x == other.x:
                # Coincidental vertical straights
                raise CoincidentStraights
            else:
                # Parallel vertical straights
                return None
        elif self.x:
            # Only the first straight is vertical
            x = self.x
            y = other.a * x + other.b
        else:
            # Only the other straight is vertical
            x = other.x
            y = self.a * x + self.b

        return Point(x, y)

    def __str__(self) -> str:
        if self.x is not None:
            return f"x = {self.x}"
        else:
            s = f"{self.a}x" if self.a != 0 else ""
            if not s:
                s = f"{self.b}"
            else:
                if self.b < 0:
                    s += f" - {abs(self.b)}"
                elif self.b > 0:
                    s += f" + {self.b}"
            return f"y = {s}"


class Star:
    """A star.
    """

    def __init__(
        self,
        center: Point,
        radius: float,
        first_corner_angle: float = 0,
        corners: int = 5,
        decimals: int = 5,
    ) -> None:
        """Initializes Star object basing on its center point, size given as
        a radius, first corner vertex slope and number of corners.

        Args:
            center (Point): center point of a star.
            radius (float): distance from center to corner vertices.
            first_corner_angle (float, optional): first vertex slope in radians.
                Defaults to 0.
            corners (int, optional): Number of corners. Defaults to 5.
            decimals (int, optional): number of decimal places for floats
            - see the explanation in Point class constructor.. Defaults to 5.
        """

        assert corners > 4, "Star should have at least 5 corners"
        assert (
            0 <= first_corner_angle <= 2 * pi
        ), "First corner slope should be between 0 and 2π"

        self.O = center
        self.r = radius
        self.first_corner_angle = round(first_corner_angle, decimals)

        # vertices
        spacing_angle = 2 * pi / corners

        corner_vertices = []
        for i in range(corners):
            corner_angle = spacing_angle * i + self.first_corner_angle
            vertex = Point(
                self.O.x + sin(corner_angle) * radius,
                self.O.y + cos(corner_angle) * radius,
            )
            corner_vertices.append(vertex)

        straights = []
        for i in range(corners):
            straight = Straight(
                corner_vertices[i], corner_vertices[(i + 2) % corners])
            straights.append(straight)

        inner_vertices = []
        for i in range(corners):
            vertex = straights[i].intersection(straights[(i - 1) % corners])
            inner_vertices.append(vertex)

        self.vertices = list(
            chain(*zip(corner_vertices, inner_vertices))
        )

    def get_x_coordinates(self) -> list[float]:
        """Provides list of x-coordinates of all star vertices, for example
        for matplotlib plotting purposes.

        Returns:
            list[float]: x-coordinates of vertices
        """
        return [v.x for v in self.vertices]

    def get_y_coordinates(self) -> list[float]:
        """Provides list of y-coordinates of all star vertices, for example
        for matplotlib plotting purposes.

        Returns:
            list[float]: y-coordinates of vertices
        """
        return [v.y for v in self.vertices]
