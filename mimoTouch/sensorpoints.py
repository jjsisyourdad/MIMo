import math

import numpy as np

from mimoEnv.utils import EPS, normalize_vectors


# TODO: function that spreads points over arbitrary mesh using spherical/cubic projection.
#       Take mujoco mesh and do intersections there?
#       Maybe mujoco raycast methods can be used here, if we can exclude other objects?

def spread_points_box(resolution: float, sizes: np.array, return_normals=False):
    """Spreads points over a box by subdividing into smaller boxes.
    Sizes is an array containing the three edge lengths of the box"""
    assert len(sizes) == 3, "Size parameter does not fit box!"
    # If distance between points is greater than size of box, have only one point in center of box
    if resolution > sizes.max():
        if return_normals:
            return np.zeros((1, 3), dtype=np.float64), np.array([0, 0, 1])
        else:
            return np.zeros((1, 3), dtype=np.float64)

    # Otherwise subdivide box into smaller boxes
    n_divisions = np.maximum(2, np.ceil(2*sizes / resolution).astype(np.int64))
    # Fill points with actual sensor positions
    x_coords = np.linspace(-sizes[0], sizes[0], n_divisions[0])
    y_coords = np.linspace(-sizes[1], sizes[1], n_divisions[1])
    z_coords = np.linspace(-sizes[2], sizes[2], n_divisions[2])

    # All points were one axis is either +1 or -1
    x0_points = [(x_coords[0], y, z) for y in y_coords for z in z_coords]
    x1_points = [(x_coords[-1], y, z) for y in y_coords for z in z_coords]
    y0_points = [(x, y_coords[0], z) for x in x_coords[1:-1] for z in z_coords]
    y1_points = [(x, y_coords[-1], z) for x in x_coords[1:-1] for z in z_coords]
    z0_points = [(x, y, z_coords[0]) for x in x_coords[1:-1] for y in y_coords[1:-1]]
    z1_points = [(x, y, z_coords[-1]) for x in x_coords[1:-1] for y in y_coords[1:-1]]

    points = x0_points + x1_points + y0_points + y1_points + z0_points + z1_points
    points = np.asarray(points)
    if not return_normals:
        return points
    else:
        x0_normals = []
        x1_normals = []
        for i in range(len(y_coords)):
            for j in range(len(z_coords)):
                if i == 0 and j == 0:
                    x0_normals.append((-1, -1, -1))
                    x1_normals.append((1, -1, -1))
                elif i == len(y_coords) - 1 and j == 0:
                    x0_normals.append((-1, 1, -1))
                    x1_normals.append((1, 1, -1))
                elif i == 0 and j == len(z_coords) - 1:
                    x0_normals.append((-1, -1, 1))
                    x1_normals.append((1, -1, 1))
                elif i == len(y_coords) - 1 and j == len(z_coords) - 1:
                    x0_normals.append((-1, 1, 1))
                    x1_normals.append((1, 1, 1))
                elif i == 0:
                    x0_normals.append((-1, -1, 0))
                    x1_normals.append((1, -1, 0))
                elif i == len(y_coords) - 1:
                    x0_normals.append((-1, 1, 0))
                    x1_normals.append((1, 1, 0))
                elif j == 0:
                    x0_normals.append((-1, 0, -1))
                    x1_normals.append((1, 0, -1))
                elif j == len(z_coords) - 1:
                    x0_normals.append((-1, 0, 1))
                    x1_normals.append((1, 0, 1))
                else:
                    x0_normals.append((-1, 0, 0))
                    x1_normals.append((1, 0, 0))

        # Next set of faces: All corners and edges with x-plane already done
        y0_normals = []
        y1_normals = []
        for k in range(1, len(x_coords)-1):
            for j in range(len(z_coords)):
                if j == 0:
                    y0_normals.append((0, -1, -1))
                    y1_normals.append((0, 1, -1))
                elif j == len(z_coords) - 1:
                    y0_normals.append((0, -1, 1))
                    y1_normals.append((0, 1, 1))
                else:
                    y0_normals.append((0, -1, 0))
                    y1_normals.append((0, 1, 0))

        z0_normals = [(0, 0, -1) for _ in range((len(x_coords)-2)*(len(y_coords)-2))]
        z1_normals = [(0, 0, 1) for _ in range((len(x_coords)-2)*(len(y_coords)-2))]

        normals = x0_normals + x1_normals + y0_normals + y1_normals + z0_normals + z1_normals
        normals = np.asarray(normals)
        normals = normalize_vectors(normals)  # Normalize
        return points, normals


def spread_points_sphere(resolution: float, radius: float, return_normals=False):
    # If resolution would lead to very small number of sensor points, instead have single point at center of sphere
    if resolution > radius:
        if return_normals:
            return np.zeros((1, 3), dtype=np.float64), np.array([0, 0, 1])
        else:
            return np.zeros((1, 3), dtype=np.float64)

    points = []

    n_theta = int(math.ceil(math.pi * radius / resolution))

    for i in range(n_theta):
        theta = (i + 0.5) * math.pi / n_theta
        n_phi = round(2 * math.pi * math.sin(theta) * radius / resolution)
        for j in range(n_phi):
            phi = 2*math.pi*j / n_phi
            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.sin(theta) * math.sin(phi)
            z = radius * math.cos(theta)
            points.append([x, y, z])

    points = np.asarray(points)
    if not return_normals:
        return points
    else:
        return points, normalize_vectors(points)


# TODO: Proper points instead of spherical projection
def spread_points_ellipsoid(resolution: float, radii, return_normals=False):
    """ Spread points over an ellipsoid using a spherical projection. radii should be list/array (a, b, c), where
    a is the x-radius, b the y-radius and c the z-radius"""
    max_r = np.max(radii)
    # If resolution would lead to very small number of sensor points, instead have single point at center of sphere
    if resolution > max_r:
        if return_normals:
            return np.zeros((1, 3), dtype=np.float64), np.array([0, 0, 1])
        else:
            return np.zeros((1, 3), dtype=np.float64)

    points = []
    normals = []

    n_theta = int(math.ceil(math.pi * max_r / resolution))

    for i in range(n_theta):
        theta = (i + 0.5) * math.pi / n_theta
        n_phi = round(2 * math.pi * math.sin(theta) * max_r / resolution)
        for j in range(n_phi):
            phi = 2*math.pi*j / n_phi
            x = radii[0] * math.sin(theta) * math.cos(phi)
            y = radii[1] * math.sin(theta) * math.sin(phi)
            z = radii[2] * math.cos(theta)
            points.append([x, y, z])
            normals.append([x / (radii[0] * radii[0]), y / (radii[1] * radii[1]), z / (radii[2] * radii[2])])

    points = np.asarray(points)
    if return_normals:
        return points, normalize_vectors(np.asarray(normals))
    else:
        return points


def _spread_points_pipe(resolution: float, length: float, radius: float):
    """ Spreads points around the outer surface of a cylinder, without caps. Always returns normal vectors. """
    # Number of subdivisions along length
    n_length = int(math.ceil(length / resolution)) + 1
    # Number of subdivisions around circumference
    n_circum = int(math.ceil(2 * math.pi * radius / resolution))

    points = []
    normals = []
    for i in range(n_length):
        if n_length == 1:
            z = 0
        else:
            z = (i * length / (n_length - 1)) - length / 2
        for j in range(n_circum):
            theta = 2 * math.pi * j / n_circum
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            points.append([x, y, z])
            normals.append([x, y, 0])

    return np.asarray(points), np.asarray(normals)


def spread_points_pipe(resolution: float, length: float, radius: float, return_normals=False):
    points, normals = _spread_points_pipe(resolution, length, radius)
    if return_normals:
        return points, normalize_vectors(normals)
    else:
        return points


def spread_points_cylinder(resolution: float, length: float, radius: float, return_normals=False):
    """ Spreads points around the outer surface of a cylinder, including caps """
    # Number of subdivisions along length
    n_length = int(math.ceil(length / resolution))
    # Number of subdivisions around circumference
    n_circum = int(math.ceil(2 * math.pi * radius / resolution))
    # Number of rings on caps
    n_caps = int(round(radius / resolution)) + 1

    # If resolution is too low to cover cylinder at least roughly, return single point centered on cylinder
    if n_circum < 3 or n_length < 2:
        points = np.zeros((1, 3), dtype=np.float64)
        normals = np.array([0, 0, 1])

    else:
        pipe_points, pipe_normals = _spread_points_pipe(resolution, length, radius)
        pipe_normals = normalize_vectors(pipe_normals)
        # Adjust normals for points at the edge of the pipe
        max_z = np.max(pipe_points[:, 2])
        min_z = np.min(pipe_points[:, 2])
        max_idx = pipe_points[:, 2] == max_z
        min_idx = pipe_points[:, 2] == min_z
        pipe_normals[max_idx, 2] = 1.
        pipe_normals[min_idx, 2] = -1.

        # Caps
        cap_points = []
        cap_normals = []
        if n_caps > 1:
            cap_radii = np.linspace(0, radius, n_caps)
            # Go through the radii, except for the outermost, which we already covered
            for cap_radius in cap_radii[:-1]:
                # Calculate the number of subdivisions
                if abs(cap_radius) < EPS:
                    n_cap_circum = 1
                else:
                    n_cap_circum = int(math.floor(2 * math.pi * cap_radius / resolution))
                for j in range(n_cap_circum):
                    theta = 2 * math.pi * (j + 0.5) / n_cap_circum
                    x = cap_radius * math.cos(theta)
                    y = cap_radius * math.sin(theta)
                    cap_points.append([x, y, -length / 2])
                    cap_points.append([x, y, length / 2])
                    cap_normals.append([0, 0, -1])
                    cap_normals.append([0, 0, 1])
        if len(cap_points) > 0:
            cap_points = np.asarray(cap_points)
            cap_normals = np.asarray(cap_normals)
            points = np.concatenate([pipe_points, cap_points])
            normals = np.concatenate([pipe_normals, cap_normals])
        else:
            points = pipe_points
            normals = pipe_normals

    if return_normals:
        return points, normalize_vectors(normals)
    else:
        return points


def spread_points_capsule(resolution: float, length: float, radius: float, return_normals=False):
    # Number of subdivisions around circumference
    n_circum = int(math.ceil(2 * math.pi * radius / resolution))

    # If resolution is too low to cover geom at least roughly, return single point centered on cylinder
    if n_circum < 3:
        points = np.zeros((1, 3), dtype=np.float64)
        normals = np.array([0, 0, 1])

    else:
        pipe_points, pipe_normals = _spread_points_pipe(resolution, length, radius)

        # Two half-spheres with open edge already covered
        sphere_points = []
        sphere_normals = []
        n_theta = int(round(math.pi * radius / (2*resolution)))
        for i in range(n_theta):
            theta = (i + 0) * math.pi / (2*n_theta)
            n_phi = round(2 * math.pi * math.sin(theta) * radius / resolution)
            if n_phi < 2:
                z = length / 2 + radius
                sphere_points.append([0, 0, z])
                sphere_points.append([0, 0, -z])
                sphere_normals.append([0, 0, 1])
                sphere_normals.append([0, 0, -1])
            else:
                for j in range(n_phi):
                    phi = 2 * math.pi * j / n_phi
                    x = radius * math.sin(theta) * math.cos(phi)
                    y = radius * math.sin(theta) * math.sin(phi)
                    z_normals = radius * math.cos(theta)
                    z = z_normals + length / 2  # half spheres at end of cylinder
                    sphere_points.append([x, y, z])
                    sphere_points.append([x, y, -z])
                    sphere_normals.append([x, y, z_normals])
                    sphere_normals.append([x, y, -z_normals])

        points = np.concatenate([pipe_points, np.asarray(sphere_points)])
        normals = np.concatenate([pipe_normals, np.asarray(sphere_normals)])

    if return_normals:
        return points, normalize_vectors(normals)
    else:
        return points
