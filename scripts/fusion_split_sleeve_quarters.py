# Fusion helper: split SphereSleeve into 4 longitude quarters for south SubModules.
# Run from Fusion MCP / Scripts after Glorb Cups Assembly is open.
#
# Findings:
#   Sleeve intersects SubModule4,5,6,7 (all four southern patches).
#   North SubModule0–3: cups only.
#
# Map: SleeveQ0→SubModule4, Q1→5, Q2→6, Q3→7
# Column hole = existing sleeve ID (Ø22.4 mm); keep as printed bore.

import math
import adsk.core
import adsk.fusion


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    sleeve_occ = None
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        if occ.component.name == "SphereSleeve":
            sleeve_occ = occ
            break
    if not sleeve_occ:
        raise RuntimeError("SphereSleeve not found")

    i = root.occurrences.count - 1
    while i >= 0:
        occ = root.occurrences.item(i)
        n = occ.component.name
        if n.startswith("SleeveQ"):
            occ.deleteMe()
        i -= 1

    src_body = sleeve_occ.bRepBodies.item(0)

    def copy_sleeve(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        result = src_body.copyToComponent(occ)
        body = result if isinstance(result, adsk.fusion.BRepBody) else result.item(0)
        body.name = name + "Body"
        return occ

    quarters = []
    for q in range(4):
        quarters.append((q, copy_sleeve(f"SleeveQ{q}")))

    sleeve_occ.isLightBulbOn = False

    for q, occ in quarters:
        comp = occ.component
        a0 = q * 90.0
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = f"Wedge{q}"
        r = 10.0

        def pt(deg):
            rad = math.radians(deg)
            return adsk.core.Point3D.create(r * math.cos(rad), r * math.sin(rad), 0)

        lines = sk.sketchCurves.sketchLines
        arcs = sk.sketchCurves.sketchArcs
        o = adsk.core.Point3D.create(0, 0, 0)
        p0, p1 = pt(a0), pt(a0 + 90.0)
        lines.addByTwoPoints(o, p0)
        lines.addByTwoPoints(o, p1)
        arcs.addByCenterStartSweep(o, p0, math.radians(90.0))
        prof = max(
            (sk.profiles.item(i) for i in range(sk.profiles.count)),
            key=lambda p: abs(p.areaProperties().area),
        )
        ext = comp.features.extrudeFeatures
        e_in = ext.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        e_in.setTwoSidesDistanceExtent(
            adsk.core.ValueInput.createByReal(20.0),
            adsk.core.ValueInput.createByReal(20.0),
        )
        wedge = ext.add(e_in).bodies.item(0)

        target = None
        for bi in range(comp.bRepBodies.count):
            b = comp.bRepBodies.item(bi)
            if b != wedge:
                target = b
                break
        tool_col = adsk.core.ObjectCollection.create()
        tool_col.add(wedge)
        comb = comp.features.combineFeatures.createInput(target, tool_col)
        comb.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        comb.isKeepToolBodies = False
        comp.features.combineFeatures.add(comb)
        sk.isVisible = False
        b = comp.bRepBodies.item(0)
        bb = b.boundingBox
        print(
            f"SleeveQ{q}: vol={b.volume:.4f} z={bb.minPoint.z*10:.1f}..{bb.maxPoint.z*10:.1f}"
        )

    print("Map: SleeveQ0->SubModule4, Q1->5, Q2->6, Q3->7")
