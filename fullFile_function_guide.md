# Function guide for `fullFile.py`

This guide describes the functions in [`fullFile.py`](./fullFile.py), grouped by the class or module where each function is defined. Positions and distances are generally in kilometres, and velocities are in kilometres per second.

## Module-level vector and coordinate helpers

| Function | What it does |
|---|---|
| [`unit(v)`](./fullFile.py#L15) | Returns a unit-length vector pointing in the same direction as `v`. |
| [`scale(s, v)`](./fullFile.py#L20) | Multiplies every component of vector `v` by `s`. |
| [`norm(v)`](./fullFile.py#L24) | Returns the length (magnitude) of vector `v`. |
| [`mid(a, b)`](./fullFile.py#L28) | Finds the midpoint along the spherical arc between points `a` and `b`. |
| [`chord(a, b)`](./fullFile.py#L32) | Returns the straight-line distance between points `a` and `b`. |
| [`sub(u, v)`](./fullFile.py#L36) | Subtracts vector `v` from vector `u`, component by component. |
| [`add(u, v)`](./fullFile.py#L38) | Adds vectors `u` and `v`, component by component. |
| [`cross(u, v)`](./fullFile.py#L42) | Returns the cross product of vectors `u` and `v`. |
| [`dot(u, v)`](./fullFile.py#L44) | Returns the dot product of vectors `u` and `v`. |
| [`toPolar(v)`](./fullFile.py#L49) | Converts a 3D point to `(radius, latitude, longitude)`, with angles in degrees. |
| [`fromPolar(r, lat, lon)`](./fullFile.py#L54) | Converts a radius, latitude, and longitude (angles in degrees) into a 3D point. |

## `SpaceObject`

Represents an object with an ID, a 3D position, and a velocity.

| Function | What it does |
|---|---|
| [`__init__(id, x, y, z, vx, vy, vz)`](./fullFile.py#L63) | Creates the object. The `z`, `vx`, `vy`, and `vz` values default to zero. |
| [`advance(dt)`](./fullFile.py#L69) | Moves the object forward by `dt` seconds, assuming its velocity stays constant. |
| [`__eq__(other)`](./fullFile.py#L73) | Checks whether another object has the same ID. |
| [`__lt__(other)`](./fullFile.py#L74) | Compares objects by their IDs, converted to strings. |
| [`__le__(other)`](./fullFile.py#L75) | Checks whether this object's ID is less than or equal to the other's. |
| [`squareDist(other)`](./fullFile.py#L77) | Returns the squared distance to another object, without calculating a square root. |
| [`asTuple()`](./fullFile.py#L80) | Returns the ID, position, and velocity as a tuple. |
| [`__str__()`](./fullFile.py#L83) | Returns a readable string showing the object's ID and position. |
| [`__repr__()`](./fullFile.py#L86) | Returns the object's ID as its representation, such as when it appears in a list. |
| [`__hash__()`](./fullFile.py#L89) | Returns a hash based on the ID, allowing objects to be used in sets and as dictionary keys. |

## `OrbitObject`

Inherits from `SpaceObject` and represents an object moving at constant speed on a circular orbit around the origin.

| Function | What it does |
|---|---|
| [`__init__(id, x, y, z, vx, vy, vz)`](./fullFile.py#L94) | Initializes the inherited object fields and records its distance `r` from the origin. |
| [`advance(dt)`](./fullFile.py#L104) | Advances the object along its orbit for `dt` seconds, updating its position and velocity. It also clears cached latitude and longitude values. |
| [`getPolarCoords()`](./fullFile.py#L115) | Returns `(radius, latitude, longitude)`. It calculates and caches latitude and longitude if they have not been computed since the last move. |
| [`fromPolarCords(cls, id, r, lat, lon, vx, vy, vz)`](./fullFile.py#L123) | Class method that creates an orbit object from polar coordinates and an optional velocity. |
| [`__str__()`](./fullFile.py#L127) | Returns a readable string showing the object's ID and polar coordinates. |

## `Box`

Represents a rectangular 2D region, used by a quadtree.

| Function | What it does |
|---|---|
| [`__init__(c0, c1, name)`](./fullFile.py#L132) | Creates a box from two opposite corners and a name; stores its corners and width. |
| [`isIn(p)`](./fullFile.py#L139) | Checks whether a space object's x/y position is inside the box. Boundaries count as inside. |
| [`_isIn(p)`](./fullFile.py#L142) | Checks whether an `(x, y)` coordinate tuple is inside the box. |
| [`touch(other)`](./fullFile.py#L147) | Checks whether this box and another box overlap or touch, including at their boundaries. |
| [`asTuple()`](./fullFile.py#L154) | Returns the box bounds as `(x0, y0, x1, y1)`. |
| [`split4()`](./fullFile.py#L158) | Divides the box into four child boxes in the order northeast, northwest, southwest, southeast. |
| [`__str__()`](./fullFile.py#L167) | Returns a readable string describing the box. |

## `Trixel`

Represents a spherical triangle on a sphere centered at the origin.

| Function | What it does |
|---|---|
| [`__init__(c0, c1, c2, name)`](./fullFile.py#L172) | Stores the triangle's corners, ensures their orientation is consistent, and computes its width and edge normals. |
| [`split4()`](./fullFile.py#L187) | Divides the spherical triangle into four smaller trixels. |
| [`_isIn(q)`](./fullFile.py#L197) | Checks whether a 3D point is inside the trixel, allowing a small tolerance for floating-point imprecision. |
| [`isIn(p)`](./fullFile.py#L204) | Checks whether a space object's 3D position is inside the trixel. |
| [`touch(other)`](./fullFile.py#L209) | Checks whether this trixel and another trixel overlap or touch, including at their edges. |
| [`__str__()`](./fullFile.py#L217) | Returns a readable string describing the trixel using its corners' latitude and longitude. |

## `QNode`

A quadtree node. It contains a `Box` and is either a leaf holding objects or an internal node with four children.

| Function | What it does |
|---|---|
| [`__init__(box)`](./fullFile.py#L223) | Creates a leaf node with the given box and an empty object list. |
| [`niceStr()`](./fullFile.py#L232) | Builds a text drawing of the node and its descendants. |
| [`plot(ax, ids, figsize)`](./fullFile.py#L254) | Draws the node's boxes and objects using Matplotlib. If `ids=True`, it labels the objects. If no axes are supplied, it creates and displays a figure. |

## `HTMNode`

A hierarchical triangular mesh node. It contains a `Trixel` and is either a leaf holding orbit objects or an internal node with four children.

| Function | What it does |
|---|---|
| [`__init__(trixel)`](./fullFile.py#L282) | Creates a leaf node with the given trixel and an empty object list. |
| [`niceStr()`](./fullFile.py#L291) | Builds a text drawing of the node and its descendants. |
| [`plot(ax, ids, res, below)`](./fullFile.py#L313) | Draws the spherical trixel, its descendants, and contained objects using Matplotlib. `res` controls shading resolution, `ids` enables object labels, and `below` places the title below the drawing. |

## `ArrayList`

A simple wrapper around a Python list, included for use in this coursework.

| Function | What it does |
|---|---|
| [`__init__()`](./fullFile.py#L360) | Creates an empty list. |
| [`get(i)`](./fullFile.py#L361) | Returns the item at index `i`. |
| [`set(i, e)`](./fullFile.py#L362) | Replaces the item at index `i` with `e`. |
| [`length()`](./fullFile.py#L363) | Returns the number of items. |
| [`append(e)`](./fullFile.py#L364) | Adds `e` to the end of the list. |
| [`remove(i)`](./fullFile.py#L365) | Removes and returns the item at index `i`. |
| [`toArray()`](./fullFile.py#L366) | Returns a copy of the underlying Python list. |
| [`__str__()`](./fullFile.py#L367) | Returns the contents as a string. |

## `NaiveCDS`

A basic collision-detection system that stores a list of bodies.

| Function | What it does |
|---|---|
| [`__init__(bodies)`](./fullFile.py#L376) | Stores the bodies to track. |
| [`advanceBodies(dt)`](./fullFile.py#L380) | Advances every body by `dt` seconds by calling its `advance` method. |
| [`warnings(CT)`](./fullFile.py#L385) | Intended to return each pair of object IDs whose distance is less than `CT`. This function is currently unfinished (`pass`). |
| [`run(total_time, dt, CT)`](./fullFile.py#L390) | Intended to return warnings at times `0`, `dt`, `2*dt`, and so on through `total_time`. This function is currently unfinished (`pass`). |

## Notes

| Topic | Details |
|---|---|
| `dt` | The time interval, in seconds, used to advance objects. |
| `CT` | The distance threshold, in kilometres, used by `warnings`; pairs closer than this threshold should be reported. Python is case-sensitive, so `CT` and `ct` are different names. |
| Plotting dependencies | The `plot` methods import Matplotlib when called. They also call `QuadTree._collect` or `HTMTree._collect`, which are not defined in this file. |
