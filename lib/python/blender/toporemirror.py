import bpy
from bpy import context as C
from bpy import data as D

import math
import bmesh

import mathutils
from mathutils import Vector, Quaternion, Matrix
import numpy as np

from time import perf_counter

obj = D.objects["Base_Mean.004"]


# Failed angle-based edgewalk, could possibly works but hit
# issues with angle sorting where (-pi-x) should equal (-x)
# but not (pi-x) etc. It tries to match edges of verts by
# their normal-aligned rotation.
def topowalk(obj, center_thresh=0.0001):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    # bm.edges.ensure_lookup_table()
    # bm.loops.ensure_lookup_table()

    cs = []
    ls = []
    rs = []
    for i, v in enumerate(bm.verts):
        x = v.co.x
        if x < -center_thresh:
            ls.append(i)
        elif x > center_thresh:
            rs.append(i)
        else:
            cs.append(i)

    vseen = np.full((len(bm.verts)), False)
    vseen[ls + cs] = True

    delta = Vector([1, 0, 0])  # (v1.co - v0.co)#.normalized()

    def edgewalk(i0, i1):
        # i0, i1 = pair
        v0, v1 = bm.verts[i0], bm.verts[i1]

        up = Vector([0, 0, 1])
        up2d = Vector([-1, 0])

        def _angle2d_normal_sorted_evidx(bv, neg=False):
            rd = bv.normal.rotation_difference(up).to_matrix()
            angles = []

            for e in bv.link_edges:
                ev = e.other_vert(bv)
                eco = (rd @ (ev.co - bv.co).normalized()).to_2d()
                # eco = Vector([eco.x, eco.y])
                if neg: eco.x = -eco.x
                # if neg:
                angles.append((ev.index, eco.angle_signed(up2d)))
            #            else:
            #                angles.append((ev.index, eco.angle_signed(up2d)))
            return [x[0] for x in sorted(angles, key=lambda x: x[1])]
            # return sorted(angles, key=lambda x: x[1])

        evs0 = _angle2d_normal_sorted_evidx(v0)
        evs1 = _angle2d_normal_sorted_evidx(v1, neg=True)
        return zip(evs0, evs1)

        #        evs0 = [e.other_vert(v0) for e in v0.link_edges]
        #        evs1 = [e.other_vert(v1) for e in v1.link_edges]

        if len(evs0) != len(evs1):
            print(f"ERR: uneq edges for v0, v1: {v0.index}, {v1.index}: {[ev for ev in evs0]}, {[ev for ev in evs1]}")

        # evs0.sort(key=lambda ev: (ev.co - v0.co).angle(delta))
        # evs1.sort(key=lambda ev: (ev.co - v1.co).angle(-delta))

        #        evs0.sort(key=lambda ev: ev.co.angle(v0.normal))
        #        evs1.sort(key=lambda ev: ev.co.angle(v1.normal))
        #
        #        rd0 = delta.rotation_difference(v0.normal)
        #        rd1 = delta.rotation_difference(v1.normal)
        #
        #
        #        return zip([ev.index for ev in evs0], [ev.index for ev in evs1])
        result = []
        for i, ev0 in enumerate(evs0):
            if vseen[ev0]: continue
            result.append((ev0, evs1[i]))
            vseen[ev0] = True

        return result
        # angles0 = [(ev.index, (ev.co - v0.co).angle(delta)) for ev in evs0]
        # angles1 = [(ev.index, (ev.co - v1.co).angle(-delta)) for ev in evs1]

        # Gave the same order but less difference, maybe more error?
        # angles0 = [(ev.index, ev.co.angle(delta)) for ev in evs0]
        # angles1 = [(ev.index, ev.co.angle(-delta)) for ev in evs1]
        # angles0.sort(key=lambda x: x[1])
        # angles1.sort(key=lambda x: x[1])

    i0 = 9733
    i1 = 9733
    # (9732, 20361)
    # i0, i1 = 5543, 29652

    # [(3883, 28005), (5850, 29953), (5542, 29651), (5544, 29653)]
    # i0,i1 = 6210,6210
    print(list(edgewalk(i0, i1)))
    bv0 = bm.verts[i0]
    bv1 = bm.verts[i1]
    #
    up = Vector([0, 0, 1])
    up2d = Vector([-1, 0])

    def evs_anglesorted(bv, neg=False):
        rd = bv.normal.rotation_difference(up).to_matrix()
        angles = []

        for e in bv.link_edges:
            ev = e.other_vert(bv)
            eco = (rd @ (ev.co - bv.co).normalized()).to_2d()
            # eco = Vector([eco.x, eco.y])
            if neg: eco.x = -eco.x
            # if neg:
            #            angles.append((ev.index, eco.angle_signed(up2d)))
            angles.append((ev.index, Vector(np.round(eco)).angle_signed(up2d) / math.pi))
        #            else:
        #                angles.append((ev.index, eco.angle_signed(up2d)))
        # return [x[0] for x in sorted(angles, key=lambda x: x[1])]
        return sorted(angles, key=lambda x: x[1])

    ang0 = evs_anglesorted(bv0)
    ang1 = evs_anglesorted(bv1, neg=True)

    print(ang0)
    print(ang1)

    bm.free()
    return True
    # known_pairs = [(i, i) for i in cs]
    from queue import Queue
    q = Queue()
    for i in cs: q.put((i, i))
    # add_pairs = []
    # topo = np.full((len(bm.verts)), 0, dtype=np.uint32)
    topo = dict()

    t = perf_counter()
    # n_items_time = len(known_pairs)
    n_iter = 0  # -len(cs)

    while not q.empty():
        i0, i1 = q.get()
        topo[i0] = i1
        new_pairs = edgewalk(i0, i1)
        for newp in new_pairs:
            q.put(newp)

        n_iter += 1
        if n_iter > len(vseen):
            print("n_iter > len(vseen): BREAKING EARLY")
            break

    dt = perf_counter() - t
    print(f"{dt:.4g} s")  # | {dt/n_items_time:.5g} s / item")

    bm.free()
    return topo


# Fast but inaccurate, not topological
def topo_kddist(obj):
    ls = [v for v in obj.data.vertices if v.co.x < -0.0001]
    rs = [v for v in obj.data.vertices if v.co.x > 0.0001]

    kd = mathutils.kdtree.KDTree(len(rs))
    for v in rs:
        kd.insert(v.co, v.index)

    kd.balance()

    mapping = dict()

    for v in ls:
        target = v.co.copy()
        target.x = math.fabs(target.x)

        _, index, _ = kd.find(target)

        mapping[v.index] = index

    return mapping


def topo_distsort(obj):
    ls = [v for v in obj.data.vertices if v.co.x < -0.0001]
    rs = [v for v in obj.data.vertices if v.co.x > 0.0001]

    dist_l = np.array([l.co.magnitude for l in ls])
    dist_r = np.array([r.co.magnitude for r in rs])

    sort_l = np.argsort(dist_l)
    sort_r = np.argsort(dist_r)

    mapping = dict()

    for i in range(len(sort_l)):
        indl = ls[sort_l[i]].index
        indr = rs[sort_r[i]].index
        mapping[indl] = indr

    return mapping


from queue import Queue


def topo_edgering(obj, center_thresh=0.0001, transform=False):
    # Add shapekeys for mirrors
    if transform:
        obj.shape_key_add(name="Basis", from_mix=False)
        obj.shape_key_add(name="left", from_mix=False)
        obj.shape_key_add(name="right", from_mix=False)

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    if transform:
        left_key = bm.verts.layers.shape["left"]
        right_key = bm.verts.layers.shape["right"]

    cs = []
    ls = []
    rs = []
    for i, v in enumerate(bm.verts):
        x = v.co.x
        if x < -center_thresh:
            ls.append(i)
        elif x > center_thresh:
            rs.append(i)
        else:
            cs.append(i)

    edge_seen = np.full(len(bm.edges), False)
    testpairs = [(6528, 6528, 0)]

    centerpairs = []
    topo = np.full(len(bm.verts), -1, dtype=np.int32)

    for ci in cs:
        cv = bm.verts[ci]
        for edge in cv.link_edges:
            if edge_seen[edge.index]: continue
            if edge.other_vert(cv).index in cs:
                edge_seen[edge.index] = True
                topo[cv.index] = cv.index
                centerpairs.append((edge.index, edge.index))

    def _unconnected_edge(face, edge):
        _inds = [v.index for v in edge.verts]
        for fe in face.edges:
            if not any(v.index in _inds for v in fe.verts):
                return fe

    def _next_edge_center(edge, negative=True):
        f0 = edge.link_faces[0]
        f1 = edge.link_faces[1]
        e0 = _unconnected_edge(f0, edge)
        if edge_seen[e0.index]:
            return _unconnected_edge(f1, edge)

        if negative:
            if any(v.co.x > center_thresh for v in e0.verts):
                return _unconnected_edge(f1, edge)
        else:
            if any(v.co.x < -center_thresh for v in e0.verts):
                return _unconnected_edge(f1, edge)

        return e0

    def _next_edge(edge):
        f0 = edge.link_faces[0]
        e0 = _unconnected_edge(f0, edge)
        if edge_seen[e0.index]:
            return _unconnected_edge(edge.link_faces[1], edge)
        return e0

    def _connected_vert(vert, edge):
        _inds = [v.index for v in edge.verts]
        for v in (ve.other_vert(vert) for ve in vert.link_edges):
            if v.index in _inds:
                return v, 0 if edge.verts[0] == v else 1

    def _v_edge(v0, v1):
        for e in v0.link_edges:
            if e.other_vert(v0) == v1:
                return e, 0 if e.verts[0] == v0 else 1

    edgepairs = Queue()

    vbreaks = 0
    fn4break = 0
    topoadd = 0
    iter = 0

    for ei0, ei1 in centerpairs:
        e0 = bm.edges[ei0]
        e1 = bm.edges[ei1]

        ne0 = _next_edge_center(e0)
        ne1 = _next_edge_center(e1, negative=False)

        edge_seen[ne0.index] = True
        edge_seen[ne1.index] = True

        v0_0 = e0.verts[0]
        v0_1 = e0.verts[1]
        v1_0 = e1.verts[0]
        v1_1 = e1.verts[1]

        nv0_0, i0 = _connected_vert(v0_0, ne0)
        nv1_0, i1 = _connected_vert(v1_0, ne1)
        nv0_1 = ne0.verts[(i0 + 1) % 2]
        nv1_1 = ne1.verts[(i1 + 1) % 2]

        nvi = i0 - i1  # 0 if i0 == i1, 1 if i0 != i1

        topo[v0_0.index] = v1_0.index
        topo[v0_1.index] = v1_1.index
        topo[v1_0.index] = v0_0.index
        topo[v1_1.index] = v0_1.index

        edgepairs.put((ne0.index, ne1.index, nvi))

    # for ei0, ei1, vi in testpairs:
    while not edgepairs.empty():
        ei0, ei1, vi = edgepairs.get()
        e0 = bm.edges[ei0]
        e1 = bm.edges[ei1]

        # Add verts we know match
        v0_0 = e0.verts[0]
        v0_1 = e0.verts[1]
        if vi == 0:
            v1_0 = e1.verts[0]
            v1_1 = e1.verts[1]
        else:
            v1_0 = e1.verts[1]
            v1_1 = e1.verts[0]

        topo[v0_0.index] = v1_0.index
        topo[v0_1.index] = v1_1.index
        topo[v1_0.index] = v0_0.index
        topo[v1_1.index] = v0_1.index
        topoadd += 1

        ne0 = _next_edge(e0)
        if edge_seen[ne0.index]: continue
        ne1 = _next_edge(e1)

        edge_seen[ne0.index] = True
        edge_seen[ne1.index] = True

        if any(len(f.edges) != 4 for f in e0.link_faces) \
                or any(len(f.edges) != 4 for f in e1.link_faces):
            # fn4break += 1
            continue

        # New verts
        nv0_0, i0 = _connected_vert(v0_0, ne0)
        nv1_0, i1 = _connected_vert(v1_0, ne1)
        nv0_1 = ne0.verts[(i0 + 1) % 2]
        nv1_1 = ne1.verts[(i1 + 1) % 2]

        nvi = i0 - i1  # 0 if i0 == i1, 1 if i0 != i1

        edgepairs.put((ne0.index, ne1.index, nvi))

        # Side edges
        #        e0_0, i0_0 = _v_edge(v0_0, nv0_0)
        #        e1_0, i1_0 = _v_edge(v1_0, nv1_0)
        #        vi0 = i0_0 - i1_0
        #
        #        e0_1, i0_1 = _v_edge(v0_1, nv0_1)
        #        e1_1, i1_1 = _v_edge(v1_1, nv1_1)
        #        vi1 = i0_1 - i1_1

        #        edge_seen[e0_0.index] = True
        #        edge_seen[e0_1.index] = True
        #        edge_seen[e1_0.index] = True
        #        edge_seen[e1_1.index] = True

        # edgepairs.put((e0_0.index, e1_0.index, vi0))
        # edgepairs.put((e0_1.index, e1_1.index, vi1))

        iter += 1
        if iter > len(bm.verts):
            print("Overiter!!!")
            break

    seenedges = 0
    for b in edge_seen:
        if not b: seenedges += 1
    print(f"Iter: {iter}, Vbreaks: {vbreaks}, Fn4break: {fn4break}, Topoadd: {topoadd}")
    print(f"Seen edges: {seenedges} / {len(bm.edges)}")

    def _transform_key(i, key):
        oi = topo[i]
        vert = bm.verts[i]
        nco = bm.verts[oi].co.copy()
        nco.x = -nco.x
        vert[key] = nco

    if transform:
        for li in ls:
            _transform_key(li, left_key)
        for ri in rs:
            _transform_key(ri, right_key)

    bm.to_mesh(obj.data)
    bm.free()
    return topo


t = perf_counter()
ret = topofaceedge(obj, transform=True)
dt = perf_counter() - t
print(f"{dt:.4g}s")

print(ret[18956])


def select_inds(inds):
    me = C.object.data
    bm_selc = bmesh.from_edit_mesh(me)
    for vert in bm_selc.verts:
        if vert.index in inds:
            vert.select = True
        else:
            vert.select = False

    bmesh.update_edit_mesh(me)
