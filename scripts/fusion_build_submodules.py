# Fusion script: promote Cup, build CupB, create SubModule0..7 with instances.
# Invoked via Fusion MCP execute (paste/run contents).

import json
import math
import adsk.core
import adsk.fusion


TRANSFORM_PATH = r"C:\Users\maxto\Glorb\mesh\cup_instance_transforms.json"

# Shared cup params (cm)
WALL_T = 0.20
CUP_H = 2.80
FLOOR_T = 0.50
SNAP_T = 0.14
CBORE_D = 1.60
RABBET_Z = 0.15
RABBET_W = 0.12
LED_R = 0.60
R_SPHERE = 15.24


def run(_context: str):
    app = adsk.core.Application.get()

    # Part docs allow only one component — create a new Design (assembly-capable).
    active = adsk.fusion.Design.cast(app.activeProduct)
    needs_new = True
    if active:
        try:
            # Probe: Part designs reject a second component
            _tm = adsk.core.Matrix3D.create()
            _occ = active.rootComponent.occurrences.addNewComponent(_tm)
            _occ.deleteMe()
            needs_new = False
            design = active
        except Exception as ex:
            needs_new = True
            print("Active doc is Part-only; creating new Design. (%s)" % ex)

    if needs_new:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        if not design:
            design = adsk.fusion.Design.cast(app.activeProduct)
        # Name via document if possible
        try:
            doc.name = "Glorb Cups Assembly"
        except Exception:
            pass

    if not design:
        raise RuntimeError("No active design")
    root = design.rootComponent

    data = json.loads(open(TRANSFORM_PATH, encoding="utf-8").read())
    faces = data["faces"]

    # --- remove prior SubModule / Cup / CupB occurrences (re-entrant) ---
    def delete_named_root_occs(prefixes):
        i = root.occurrences.count - 1
        while i >= 0:
            occ = root.occurrences.item(i)
            name = occ.component.name
            if any(name == p or name.startswith(p) for p in prefixes):
                occ.deleteMe()
            i -= 1

    delete_named_root_occs(["SubModule", "Cup", "CupB"])

    while root.bRepBodies.count > 0:
        root.bRepBodies.item(0).deleteMe()
    while root.sketches.count > 0:
        root.sketches.item(0).deleteMe()

    i = root.constructionPlanes.count - 1
    while i >= 0:
        p = root.constructionPlanes.item(i)
        try:
            if not p.isOriginPlane:
                p.deleteMe()
        except Exception:
            pass
        i -= 1

    def make_component(name):
        tm = adsk.core.Matrix3D.create()
        occ = root.occurrences.addNewComponent(tm)
        occ.component.name = name
        return occ

    def build_cup(comp, verts_xy, h_plane, body_name):
        """verts_xy: list of (x,y) in face plane, circumcenter at 0, +Z out."""
        # Clear component contents
        while comp.bRepBodies.count > 0:
            comp.bRepBodies.item(0).deleteMe()
        while comp.sketches.count > 0:
            comp.sketches.item(0).deleteMe()
        i = comp.constructionPlanes.count - 1
        while i >= 0:
            p = comp.constructionPlanes.item(i)
            try:
                if not p.isOriginPlane:
                    p.deleteMe()
            except Exception:
                pass
            i -= 1

        # Approximate inradius for inset: min distance from 0 to edges
        def dist_point_edge(px, py, ax, ay, bx, by):
            abx, aby = bx - ax, by - ay
            t = ((px - ax) * abx + (py - ay) * aby) / (abx * abx + aby * aby)
            t = max(0.0, min(1.0, t))
            qx, qy = ax + t * abx, ay + t * aby
            return math.hypot(px - qx, py - qy)

        r_in = 1e9
        n = len(verts_xy)
        for i in range(n):
            ax, ay = verts_xy[i]
            bx, by = verts_xy[(i + 1) % n]
            r_in = min(r_in, dist_point_edge(0, 0, ax, ay, bx, by))

        def inset(pts, dist):
            # Offset polygon inward by `dist` using edge normals (simple scale fallback if needed)
            # For triangles about circumcenter, uniform scale works poorly for isosceles inset.
            # Use parallel curve: each edge moved inward by dist.
            outs = []
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                cx, cy = pts[(i - 1) % n]
                # inward normals of edges i-1 and i (point toward origin roughly)
                e1x, e1y = ax - cx, ay - cy
                e2x, e2y = bx - ax, by - ay
                # left normals (CCW polygon assumed)
                n1x, n1y = -e1y, e1x
                n2x, n2y = -e2y, e2x
                L1 = math.hypot(n1x, n1y) or 1.0
                L2 = math.hypot(n2x, n2y) or 1.0
                n1x, n1y = n1x / L1, n1y / L1
                n2x, n2y = n2x / L2, n2y / L2
                # flip if pointing outward (away from origin)
                if n1x * ax + n1y * ay > 0:
                    n1x, n1y = -n1x, -n1y
                if n2x * ax + n2y * ay > 0:
                    n2x, n2y = -n2x, -n2y
                # intersection of offset lines
                # line1: through (c)+dist*n1 ... use vertex offset along angle bisector approx:
                bisx, bisy = n1x + n2x, n1y + n2y
                bl = math.hypot(bisx, bisy) or 1.0
                bisx, bisy = bisx / bl, bisy / bl
                # distance along bisector to achieve offset dist: dist / cos(halfangle)
                # cos(half) = dot(bis, n1)
                cos_h = bisx * n1x + bisy * n1y
                if abs(cos_h) < 1e-6:
                    cos_h = 1e-6
                push = dist / cos_h
                outs.append((ax + bisx * push, ay + bisy * push))
            return outs

        def scale_toward_center(pts, z):
            t = (h_plane + z) / h_plane
            return [(p[0] * t, p[1] * t) for p in pts]

        def sketch_tri(plane, name, pts):
            sk = comp.sketches.add(plane)
            sk.name = name
            lines = sk.sketchCurves.sketchLines
            p3 = [adsk.core.Point3D.create(x, y, 0) for x, y in pts]
            for i in range(3):
                lines.addByTwoPoints(p3[i], p3[(i + 1) % 3])
            return sk

        xy = comp.xYConstructionPlane
        planes = comp.constructionPlanes
        loft_feats = comp.features.loftFeatures
        ext = comp.features.extrudeFeatures

        def offset_plane(z, name):
            pin = planes.createInput()
            pin.setByOffset(xy, adsk.core.ValueInput.createByReal(z))
            pl = planes.add(pin)
            pl.name = name
            return pl

        z_bottom = -CUP_H
        z_cavity_bot = -(CUP_H - FLOOR_T)

        sk_top = sketch_tri(xy, "OuterTop", verts_xy)
        pl_bot = offset_plane(z_bottom, "BottomPlane")
        sk_bot = sketch_tri(pl_bot, "OuterBot", scale_toward_center(verts_xy, z_bottom))
        loft_in = loft_feats.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loft_in.loftSections.add(sk_top.profiles.item(0))
        loft_in.loftSections.add(sk_bot.profiles.item(0))
        loft_in.isSolid = True
        body = loft_feats.add(loft_in).bodies.item(0)
        body.name = body_name

        cav = inset(verts_xy, WALL_T)
        sk_cav_top = sketch_tri(xy, "CavityTop", cav)
        pl_cav = offset_plane(z_cavity_bot, "CavityBotPlane")
        sk_cav_bot = sketch_tri(pl_cav, "CavityBot", scale_toward_center(cav, z_cavity_bot))
        cut_in = loft_feats.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_in.loftSections.add(sk_cav_top.profiles.item(0))
        cut_in.loftSections.add(sk_cav_bot.profiles.item(0))
        cut_in.isSolid = True
        loft_feats.add(cut_in)

        rab = inset(verts_xy, RABBET_W)
        sk_rab_top = sketch_tri(xy, "RabbetTop", rab)
        pl_rab = offset_plane(-RABBET_Z, "RabbetPlane")
        sk_rab_bot = sketch_tri(pl_rab, "RabbetBot", scale_toward_center(rab, -RABBET_Z))
        rab_in = loft_feats.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
        rab_in.loftSections.add(sk_rab_top.profiles.item(0))
        rab_in.loftSections.add(sk_rab_bot.profiles.item(0))
        rab_in.isSolid = True
        loft_feats.add(rab_in)

        sk_led = comp.sketches.add(xy)
        sk_led.name = "LED12"
        sk_led.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), LED_R
        )
        e = ext.createInput(sk_led.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(z_bottom - 0.2))
        ext.add(e)

        pl_cb = offset_plane(z_bottom, "CborePlane")
        sk_cb = comp.sketches.add(pl_cb)
        sk_cb.name = "LED_Cbore"
        sk_cb.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), CBORE_D / 2.0
        )
        e2 = ext.createInput(sk_cb.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        e2.setDistanceExtent(False, adsk.core.ValueInput.createByReal(FLOOR_T - SNAP_T))
        ext.add(e2)

        for i in range(comp.sketches.count):
            comp.sketches.item(i).isVisible = False
        for i in range(comp.constructionPlanes.count):
            p = comp.constructionPlanes.item(i)
            try:
                if not p.isOriginPlane:
                    p.isLightBulbOn = False
            except Exception:
                pass
        return body

    def mat_from_face(f):
        tm = adsk.core.Matrix3D.create()
        o = f["origin"]
        x = f["xAxis"]
        y = f["yAxis"]
        z = f["zAxis"]
        tm.setWithArray(
            [
                x[0], x[1], x[2], 0.0,
                y[0], y[1], y[2], 0.0,
                z[0], z[1], z[2], 0.0,
                o[0], o[1], o[2], 1.0,
            ]
        )
        # Fusion setWithArray is row-major for 4x4; axes as rows may be wrong.
        # Prefer setToAlignCoordinateSystems:
        tm2 = adsk.core.Matrix3D.create()
        tm2.setToAlignCoordinateSystems(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Vector3D.create(1, 0, 0),
            adsk.core.Vector3D.create(0, 1, 0),
            adsk.core.Vector3D.create(0, 0, 1),
            adsk.core.Point3D.create(o[0], o[1], o[2]),
            adsk.core.Vector3D.create(x[0], x[1], x[2]),
            adsk.core.Vector3D.create(y[0], y[1], y[2]),
            adsk.core.Vector3D.create(z[0], z[1], z[2]),
        )
        return tm2

    # --- Cup A (equilateral long) ---
    EDGE_A = 9.4188
    rho_a = EDGE_A / math.sqrt(3.0)
    h_a = math.sqrt(R_SPHERE * R_SPHERE - rho_a * rho_a)
    Ra = EDGE_A / math.sqrt(3.0)
    ang0 = math.pi / 2.0
    verts_a = [
        (Ra * math.cos(ang0 + k * 2.0 * math.pi / 3.0), Ra * math.sin(ang0 + k * 2.0 * math.pi / 3.0))
        for k in range(3)
    ]

    occ_cup = make_component("Cup")
    build_cup(occ_cup.component, verts_a, h_a, "CupBody")
    occ_cup.isLightBulbOn = False  # master hidden; instances visible in SubModules

    # --- CupB (isosceles) ---
    verts_b = [(0.0, 5.0492), (-4.7095, -1.8208), (4.7094, -1.8208)]
    # circumradius of B
    rho_b = math.hypot(verts_b[0][0], verts_b[0][1])
    h_b = math.sqrt(R_SPHERE * R_SPHERE - rho_b * rho_b)
    occ_cupb = make_component("CupB")
    build_cup(occ_cupb.component, verts_b, h_b, "CupBBody")
    occ_cupb.isLightBulbOn = False

    cup_def = occ_cup.component
    cupb_def = occ_cupb.component

    # --- SubModules ---
    sm_occs = []
    for pid in range(8):
        occ = make_component(f"SubModule{pid}")
        sm_occs.append(occ)

    counts = {pid: 0 for pid in range(8)}
    for f in faces:
        pid = f["patch_id"]
        sm = sm_occs[pid].component
        tm = mat_from_face(f)
        src = cup_def if f["face_type"] == "A" else cupb_def
        inst = sm.occurrences.addExistingComponent(src, tm)
        # name occurrence for clarity
        try:
            inst.component  # linked
        except Exception:
            pass
        counts[pid] += 1

    app.activeViewport.fit()
    print("OK component tree")
    print("Cup (type A) + CupB (type B) masters hidden")
    for pid in range(8):
        print(f"  SubModule{pid}: {counts[pid]} cups")
    print(f"root occurrences: {root.occurrences.count}")
