####################################################################
# HELPER CELL
####################################################################
# Imports and given classes+utility functions to be used in your code
# DO NOT CHANGE ANY OF THE BELOW
####################################################################

import math

####################################################################
# Vector Functions. Vectors are triples (x,y,z).
####################################################################

# The unit vector for vector v.
def unit(v):
    n = math.sqrt(sum(c*c for c in v))
    return tuple(c/n for c in v)

# v scaled by the number s.
def scale(s, v):
    return tuple(s*c for c in v)

# the norm (i.e. length) of vector v
def norm(v):
    return math.hypot(*v)
    
# Midpoint of the arc a-b.
def mid(a, b):
    return scale(norm(a), unit(add(a,b)))

# Straight-line (chord) distance between points a and b.
def chord(a, b):
    return math.dist(a, b)

# Sub and add of two vectors.
def sub(u, v):
    return (u[0]-v[0], u[1]-v[1], u[2]-v[2])
def add(u, v):
    return (u[0]+v[0], u[1]+v[1], u[2]+v[2])
    
# Cross and dot product of two vectors.
def cross(u, v):
    return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
def dot(u, v):
    return sum(x*y for x, y in zip(u, v))

# Polar coordinates (r, lat, lon) of the point v: its distance r from (0,0,0), and its latitude and
# longitude in degrees (lat in [-90,90], lon in (-180,180]). At the poles the longitude is arbitrary.
def toPolar(v):
    lon = math.degrees(math.atan2(v[1], v[0]))
    return (norm(v), math.degrees(math.atan2(v[2], math.hypot(v[0], v[1]))), 180.0 if round(lon, 6) == -180 else lon)

# The point with polar coordinates (r, lat, lon), the latitude and the longitude being in degrees.
def fromPolar(r, lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (r*math.cos(la)*math.cos(lo), r*math.cos(la)*math.sin(lo), r*math.sin(la))

####################################################################
# Given Classes
####################################################################

class SpaceObject:
    def __init__(self, id, x, y, z=0, vx=0, vy=0, vz=0):
        self.id = id                             # identifier (strings)
        self.x, self.y, self.z = x, y, z         # position (km)
        self.vx, self.vy, self.vz = vx, vy, vz   # velocity (km/s)

    # Free motion: move p to its position after time dt (in place)
    def advance(self, dt):
        self.x, self.y, self.z = self.x+self.vx*dt, self.y+self.vy*dt, self.z+self.vz*dt

    # Object comparisons
    def __eq__(self, other): return str(self.id) == str(other.id)
    def __lt__(self, other): return str(self.id) < str(other.id)
    def __le__(self, other): return self < other or self == other

    def squareDist(self, other):
        return (self.x-other.x)**2+(self.y-other.y)**2+(self.z-other.z)**2

    def asTuple(self):
        return (self.id,self.x,self.y,self.z,self.vx,self.vy,self.vz)

    def __str__(self):
        return f"SpaceObject({self.id},{self.x},{self.y},{self.z})"

    def __repr__(self):
        return str(self.id)

    def __hash__(self):
        return hash(str(self.id))        

# An object moving at constant speed on a circular orbit around the Earth's centre (0,0,0).
class OrbitObject(SpaceObject):
    def __init__(self, id, x, y, z, vx, vy, vz):
        super().__init__(id, x, y, z, vx, vy, vz)
        self.r = math.sqrt(x*x + y*y + z*z)
        self.lat = self.lon = None

    # Move along the orbit for time dt (in place), keeping distance r from (0,0,0).
    # On a circular orbit the velocity v is perpendicular to the position q, and the object
    # turns by angle theta = (|v|/r)*dt in the plane of q and v:
    #     q' = cos(theta) q + sin(theta) (r/|v|) v
    #     v' = cos(theta) v - sin(theta) (|v|/r) q
    def advance(self, dt):
        self.lat = self.lon = None
        q, v = (self.x, self.y, self.z), (self.vx, self.vy, self.vz)
        s = norm(v)             # speed |v|
        if s == 0: return
        theta = s/self.r*dt
        c, sn = math.cos(theta), math.sin(theta)
        self.x, self.y, self.z = (c*q[i] + sn*(self.r/s)*v[i] for i in range(3))
        self.vx, self.vy, self.vz = (c*v[i] - sn*(s/self.r)*q[i] for i in range(3))

    # Polar values are computed when first needed and kept until the object moves.
    def getPolarCoords(self):
        if self.lat is None or self.lon is None:
            _, self.lat, self.lon = toPolar((self.x, self.y, self.z))
        return (self.r, self.lat, self.lon)

    # The orbit object with identifier id, at distance r from (0,0,0) and with latitude lat and
    # longitude lon (in degrees), and with velocity (vx,vy,vz).
    @classmethod
    def fromPolarCords(cls, id, r, lat, lon, vx=0, vy=0, vz=0):
        x, y, z = fromPolar(r, lat, lon)
        return cls(id, x, y, z, vx, vy, vz)
    
    def __str__(self):
        (r, lat, lon) = self.getPolarCoords()
        return f"OrbitObject({self.id},{self.r},{self.lat},{self.lon})"

class Box:
    def __init__(self, c0, c1, name):
        self.name = name
        (self.x0, self.y0), (self.x1, self.y1) = c0, c1
        self.corners = [c0, (self.x1,self.y0), c1, (self.x0,self.y1)]
        self.width = min(self.x1 - self.x0, self.y1 - self.y0)

    # True if p lies in this box. Boxes are closed (boundaries included).
    def isIn(self, p):
        return self._isIn((p.x,p.y))

    def _isIn(self, p):
        return self.x0 <= p[0] <= self.x1 and self.y0 <= p[1] <= self.y1
    
    # True if this box and other, boundaries included, have at least one point in common.
    # In a quadtree, this can only happen if one of its corners are in other, or viceversa.
    def touch(self, other):
        for c in self.corners:
            if other._isIn(c): return True
        for c in other.corners:
            if self._isIn(c): return True
        return False
        
    def asTuple(self):
        return (self.x0,self.y0,self.x1,self.y1)

    # Children in the fixed order [NE, NW, SW, SE].
    def split4(self):
        mx, my = (self.x0+self.x1)/2, (self.y0+self.y1)/2
        names = [f"{self.name}.{x}" for x in ["NE", "NW", "SW", "SE"]]        
        NE = Box((mx,my), (self.x1,self.y1), names[0])
        NW = Box((self.x0,my), (mx,self.y1), names[1])
        SW = Box((self.x0,self.y0), (mx,my), names[2])
        SE = Box((mx,self.y0), (self.x1,my), names[3])
        return (NE,NW,SW,SE)

    def __str__(self):
        return f"{self.name} Box(({self.x0},{self.y0}),({self.x1},{self.y1}))"

# A spherical triangle with corners c0, c1, c2: 3D points on a sphere centred at (0,0,0).
class Trixel:
    def __init__(self, c0, c1, c2, name):
        if dot(c0, cross(c1, c2)) < 0:   # keep the corners counter-clockwise seen from outside
            c1, c2 = c2, c1
        self.corners = (c0, c1, c2)
        # also store the (lat, lon) of each corner
        self.cornersPolar = tuple(toPolar(c)[1:] for c in self.corners)
        self.name = name
        # width: smallest height of the flat triangle with the same corners
        e1, e2 = sub(c1, c0), sub(c2, c0)
        twice_area = math.sqrt(dot(cross(e1, e2), cross(e1, e2)))
        self.width = twice_area / max(chord(c0, c1), chord(c1, c2), chord(c2, c0))
        # normals: normal vectors for each of the three planes containing (0,0,0) 
        # and one of the edges; useful for checking if a point is in the trixel
        self.normals = [unit(cross(c0, c1)), unit(cross(c1, c2)), unit(cross(c2, c0))]
    
    def split4(self):
        c0, c1, c2 = self.corners
        m0, m1, m2 = mid(c0, c1), mid(c1, c2), mid(c2, c0)   # mi lies on the arc from ci to c(i+1)
        names = [f"{self.name}.{x}" for x in ["C0", "C1", "C2", "MID"]]
        return [Trixel(c0, m0, m2, names[0]),     # C0: touches c0
                Trixel(c1, m1, m0, names[1]),     # C1: touches c1
                Trixel(c2, m2, m1, names[2]),     # C2: touches c2
                Trixel(m0, m1, m2, names[3])]     # MID        

    # True if point q is in the trixel, boundaries included.
    def _isIn(self, q):
        eps = 1e-9 * norm(q)  # allow some tolerance to account for float imprecision
        for i in range(3):
            if dot(self.normals[i], q) < -eps: return False
        return True

    # True if space object p is in the trixel, boundaries included.
    def isIn(self, p):
        return self._isIn((p.x, p.y, p.z))

    # True if this trixel and other have at least one point in common (edges included).
    # For trixels of a HTMTree, they touch exactly when a corner of one lies in the other.
    def touch(self, other):
        for q in self.corners:
            if other._isIn(q): return True
        for q in other.corners:
            if self._isIn(q): return True
        return False

    # The corners as (lat,lon) pairs, in degrees with at most 2 decimals, e.g. "Trixel((0,90),(90,0),(0,0))".
    def __str__(self):
        g = lambda x: f"{round(x, 2) + 0.0:g}"      # no trailing zeros, never "-0"
        return f"{self.name} Trixel(" + ",".join(f"({g(lat)},{g(lon)})" for lat, lon in self.cornersPolar) + ")"


class QNode:
    def __init__(self, box):
        self.box = box
        self.width = box.width
        self.size = 0               # number of space objects contained in node
        self.isLeaf = True          # by default new nodes are leaves
        self.bodies = ArrayList()   # leaves contain space objects
        self.children = None        # children are: [NE, NW, SW, SE]

    # Prints the node as a tree.
    def niceStr(self):
        S = ("├","─","└","│")
        angle = S[2]+S[1]+" "
        vdash = S[0]+S[1]+" "

        def niceRec(ptr,acc,pre):
            if ptr == None: raise Exception("A None QNode was found")
            val = f"{ptr.box} {ptr.size} {ptr.bodies}" if ptr.isLeaf else f"{ptr.box} {ptr.size}"
            if ptr.isLeaf: return acc+pre+val
            if pre == vdash: pre2 = S[3]+"  "
            elif pre == angle: pre2 = "   "
            else: pre2 = ""
            T = [vdash,vdash,vdash,angle]
            for i in range(4):
                T[i] = niceRec(ptr.children[i],acc+pre2,T[i])
            return acc+pre+val+"\n"+T[0]+"\n"+T[1]+"\n"+T[2]+"\n"+T[3]

        return niceRec(self,"","")

    # Draws the node's box and the boxes of all its descendants (a cross marks the centre of each internal node), and
    # the bodies of the subtree as dots (with their ids if ids=True). ax is the matplotlib axes to draw on (if None, a
    # new figure of size figsize is shown).
    def plot(self, ax=None, ids=False, figsize=(6, 6)):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        own = ax is None
        if own: fig, ax = plt.subplots(figsize=figsize)
        stack = [self]
        while stack:                                                  # the boxes of the subtree
            nd = stack.pop()
            b = nd.box
            ax.add_patch(Rectangle((b.x0, b.y0), b.x1-b.x0, b.y1-b.y0, fill=False, linewidth=0.8, alpha=0.5))
            if not nd.isLeaf:
                ax.plot((b.x0+b.x1)/2, (b.y0+b.y1)/2, linestyle='none', marker='+', markersize=9, markeredgewidth=1.8, zorder=3)
                stack += nd.children
        B = [None]*self.size                                          # the bodies of the subtree
        QuadTree._collect(self, B, 0)
        for p in B:
            ax.plot(p.x, p.y, 'o', markersize=5, color='tab:orange', zorder=4)
            if ids: ax.annotate(str(p.id), (p.x, p.y), textcoords='offset points', xytext=(4, 4), fontsize=8)
        pad = 0.05*self.box.width                                     # a small margin around the box
        ax.set_xlim(self.box.x0-pad, self.box.x1+pad)
        ax.set_ylim(self.box.y0-pad, self.box.y1+pad)
        ax.set_aspect('equal', adjustable='box')
        if own:
            plt.tight_layout()
            plt.show()


class HTMNode:
    def __init__(self, trixel):
        self.trixel = trixel
        self.width = trixel.width
        self.size = 0               # number of orbit objects contained in node
        self.isLeaf = True          # by default new nodes are leaves
        self.bodies = ArrayList()   # leaves contain orbit objects
        self.children = None        # children are: [C0, C1, C2, MID]

    # Prints the node as a tree.
    def niceStr(self):
        S = ("├","─","└","│")
        angle = S[2]+S[1]+" "
        vdash = S[0]+S[1]+" "

        def niceRec(ptr,acc,pre):
            val = f"{ptr.trixel} {ptr.size}"
            if ptr.isLeaf: return acc+pre+val+" "+str(ptr.bodies)
            if pre == vdash: pre2 = S[3]+"  "
            elif pre == angle: pre2 = "   "
            else: pre2 = ""
            T = [vdash,vdash,vdash,angle]
            for i in range(4):
                T[i] = niceRec(ptr.children[i],acc+pre2,T[i])
            return acc+pre+val+"\n"+T[0]+"\n"+T[1]+"\n"+T[2]+"\n"+T[3]

        return niceRec(self,"","")

    # Draws the node as a shaded patch of the sphere, seen from outside and slightly tilted, with the arcs of all the
    # trixels of its subtree and its bodies as dots (with their ids if ids=True). ax is the matplotlib axes to draw on
    # (a new figure is shown if it is None); res is the number of pixels per side of the shaded patch. The title, the
    # name of the trixel and its number of bodies, is above the patch, or below it if below=True.
    def plot(self, ax=None, ids=False, res=80, below=False):
        import matplotlib.pyplot as plt
        own = ax is None
        if own: fig, ax = plt.subplots(figsize=(4, 4))
        K = self.trixel.corners
        r = norm(K[0])
        comb = lambda *tv: tuple(sum(s*v[m] for s, v in tv) for m in range(3))        # linear combination of vectors
        def arcs(T):                                                                   # the sides of trixel T, as a polyline of arcs
            C = T.corners
            return [scale(r, unit(comb((1-k/16, C[i]), (k/16, C[(i+1) % 3])))) for i in range(3) for k in range(17)]
        view = unit(comb((1, unit(comb((1, K[0]), (1, K[1]), (1, K[2])))), (0.18, (0, 0, 1))))   # from outside, slightly tilted
        right = unit(cross((0, 0, 1), view))
        up = cross(view, right)
        light = unit(comb((1, view), (-0.55, right), (0.35, up)))                      # light from the upper left
        proj = lambda p: (dot(p, right), dot(p, up))                                   # position on the screen
        xy = [proj(p) for p in arcs(self.trixel)]                                      # outline of the patch
        x0, x1, y0, y1 = min(x for x, y in xy), max(x for x, y in xy), min(y for x, y in xy), max(y for x, y in xy)
        N = [cross(K[i], K[(i+1) % 3]) for i in range(3)]                              # normals of the sides, towards the inside
        def shade(x, y):                                                               # shade of the point of the sphere seen at (x,y)
            P = comb((x, right), (y, up), (math.sqrt(max(r*r - x*x - y*y, 0)), view))
            return 0.78 + 0.22*max(0, dot(P, light)/r) if all(dot(P, n) >= 0 for n in N) else float('nan')
        ax.imshow([[shade(x0 + (x1-x0)*(i+0.5)/res, y0 + (y1-y0)*(j+0.5)/res) for i in range(res)] for j in range(res)],
                  extent=(x0, x1, y0, y1), origin='lower', cmap='gray', vmin=0, vmax=1)
        stack = [(self, 1.6)]
        while stack:                                                                   # arcs of all the trixels of the subtree
            nd, lw = stack.pop()
            pts = [proj(p) for p in arcs(nd.trixel)]
            ax.plot([x for x, y in pts], [y for x, y in pts], color='k', linewidth=lw, alpha=1 if lw > 1 else 0.6)
            if not nd.isLeaf:
                stack += [(ch, 0.8) for ch in nd.children]
        B = [None]*self.size                                                           # the bodies of the subtree
        HTMTree._collect(self, B, 0)
        for p in B:
            x, y = proj((p.x, p.y, p.z))
            ax.plot(x, y, 'o', markersize=5, color='tab:orange', zorder=4)
            if ids: ax.annotate(str(p.id), (x, y), textcoords='offset points', xytext=(4, 4), fontsize=8)
        ax.axis('off')
        ax.text(0.5, -0.02 if below else 1.02, self.trixel.name + (f"  ({self.size})" if self.size > 0 else ""),
                transform=ax.transAxes, ha='center', va='top' if below else 'bottom', fontsize=10)
        if own:
            plt.tight_layout()
            plt.show()        

# A fake implementation of ArrayList that wraps a Python list.
# Not allowed in this module in general, we only use it here for convenience, 
# while we still study our ArrayList implementation in Lab 5!
class ArrayList:
    def __init__(self): self.inArray = []      
    def get(self, i): return self.inArray[i]
    def set(self, i, e): self.inArray[i] = e
    def length(self): return len(self.inArray)
    def append(self, e): self.inArray.append(e)
    def remove(self, i): return self.inArray.pop(i)
    def toArray(self): return self.inArray[:]
    def __str__(self): return str(self.toArray())


####################################################################
# Question 1: Introduction to problem and naive implementation [20 marks]
# To solve: NaiveCDS.advanceBodies, NaiveCDS.warnings, NaiveCDS.run
####################################################################

class NaiveCDS:
    def __init__(self, bodies):
        self.bodies = bodies

    # Advance every object in self.bodies by dt using its own advance function. [1.1, 5 marks]
    def advanceBodies(self, dt):
        for body in self.bodies:
            body.advance(dt)
        
    # Ids of all pairs at distance < CT, each pair once, no (p,p) pairs, any order. [1.2, 10 marks]
    def warnings(self, CT):
        warnings = []
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                if self.bodies[i].squareDist(self.bodies[j]) < CT**2:
                    if (self.bodies[j].id, self.bodies[i].id) not in warnings:
                        warnings.append((self.bodies[i].id, self.bodies[j].id))
        return warnings

    # Warnings at times 0, dt, 2dt, ..., total_time: total_time/dt + 1 arrays. [1.3, 5 marks]
    def run(self, total_time, dt, CT):
        for i in range(0, total_time + 1, dt):
            print(f"Time: {i}, Warnings: {self.warnings(CT)}")
            self.advanceBodies(dt)

####################################################################
# Question 2: Quadtrees in 2D square space [50 marks]
# To solve: QuadTree.add, QuadTree.remove, QuadTree.selection, QuadTree.warnings
####################################################################

class QuadTree:
    def __init__(self, box, CT):
        self.root = QNode(box)
        self.size = 0               # number of space objects in the tree
        self.CT = CT                # collision threshold

    # Add space object p (assumed inside the root's box). [2.1, 15 marks]
    def add(self, p):
        self.size += 1
        self.addRec(self.root,p)

    def addRec(self,node, p):
        if node.isLeaf:
            if node.width / 2 < self.CT or node.bodies.length() == 0:
                node.bodies.append(p)
                return
            else:
                # Split the node and redistribute the bodies
                node.isLeaf = False
                node.bodies = None
                node.children = [QNode(b) for b in node.box.split4()]
                
        else:
            # Add the body to the appropriate child node
            if node.children[0].box.isIn(p):
                self.addRec(node.children[0], p)
            elif node.children[1].box.isIn(p):
                self.addRec(node.children[1], p)
            elif node.children[2].box.isIn(p):
                self.addRec(node.children[2], p)
            else:
                self.addRec(node.children[3], p)
            
        
    # Remove p if present, otherwise do nothing. [2.2, 15 marks]
    def remove(self, p):
        if self.root.box.isIn(p):
            self.removeRec(self.root, p)
            self.size -= 1
        else:
            return
        
    def removeRec(self, node, p):
        if node.isLeaf:
            if p in node.bodies:
                node.bodies.remove(p)
                node.size -= 1
        
    # All space objects adjacent to p (apart from p). [2.3, 10 marks]
    # Assume that p is already in self.
    def selection(self, p):
        
        
    # Ids of all pairs at distance < CT, each pair once, no (p,p) pairs, any order. [2.4, 10 marks]
    # Must be efficient and use selection.
    def warnings(self):
        
        
    def __str__(self):
        return self.root.niceStr()

    # Collect all space objects from this QuadTree and return them in an array. [given]
    def getBodies(self):
        A = [None]*self.size
        QuadTree._collect(self.root, A, 0)
        return A

    # Copy the bodies stored under node into A from index i; return the next free index. [given]
    @staticmethod
    def _collect(node, A, i):
        if node.isLeaf:
            B = node.bodies.toArray()
            for k in range(len(B)):
                A[i] = B[k]
                i += 1
            return i
        for c in node.children:
            i = QuadTree._collect(c, A, i)
        return i

    # Draws the tree; ids=True writes the ids of the bodies. See QNode.plot. [given]
    def plot(self, figsize=(6,6), ids=False): # figsize : (w,h) in inches
        self.root.plot(ids=ids, figsize=figsize)

#Testing data

P = [None]*20
for i in range(20):
    x = 50.0 * math.cos(i * 0.3)
    y = 50.0 * math.sin(i * 0.3)
    P[i] = SpaceObject(str(i), x, y)

q = QuadTree(Box((-50,-50),(50,50),"R"), 25)
for p in P: q.add(p)
print(q);