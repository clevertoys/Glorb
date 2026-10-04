# Rebuild Glorb Column (stepped Ø22/Ø28, ridge at south pole). Units: cm.
# Entry: rebuild_column() — not run(), so Fusion MCP won't auto-invoke.

import adsk.core
import adsk.fusion


def rebuild_column():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError("No design")
    root = design.rootComponent

    # Spec (cm)
    R_POLE = -15.24  # south-pole ridge Z
    OD_IN = 2.20
    OD_BASE = 2.80
    ID = 1.60
    INTO = 5.08  # 2 in into sphere
    BELOW = 10.0  # 100 mm below ridge

    z_top = R_POLE + INTO  # -10.16
    z_ridge = R_POLE
    z_bot = R_POLE - BELOW  # -25.24

    # Find or create Column component
    occ = None
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        if o.component.name == "Column":
            occ = o
            break
    if occ is None:
        tm = adsk.core.Matrix3D.create()
        occ = root.occurrences.addNewComponent(tm)
        occ.component.name = "Column"
    col = occ.component

    # Clear bodies / sketches / non-origin planes
    while col.bRepBodies.count > 0:
        col.bRepBodies.item(0).deleteMe()
    while col.sketches.count > 0:
        col.sketches.item(0).deleteMe()
    i = col.constructionPlanes.count - 1
    while i >= 0:
        p = col.constructionPlanes.item(i)
        try:
            if not p.isOriginPlane:
                p.deleteMe()
        except Exception:
            pass
        i -= 1

    New = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    Join = adsk.fusion.FeatureOperations.JoinFeatureOperation
    xy = col.xYConstructionPlane

    def extrude_at(name, radius, z0, height, op):
        pin = col.constructionPlanes.createInput()
        pin.setByOffset(xy, adsk.core.ValueInput.createByReal(z0))
        pl = col.constructionPlanes.add(pin)
        pl.name = name + "Pl"
        sk = col.sketches.add(pl)
        sk.name = name
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), radius
        )
        e = col.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
        e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
        feat = col.features.extrudeFeatures.add(e)
        sk.isVisible = False
        return feat

    # Ø28 below ridge + Ø22 into sphere (scoped Join — DM Join hits all bodies)
    extrude_at("ColBase", OD_BASE / 2.0, z_bot, BELOW, New)
    body = col.bRepBodies.item(0)
    # upper segment as NewBody then Combine-join
    pin = col.constructionPlanes.createInput()
    pin.setByOffset(xy, adsk.core.ValueInput.createByReal(z_ridge))
    pl = col.constructionPlanes.add(pin)
    sk = col.sketches.add(pl)
    sk.name = "ColIn"
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), OD_IN / 2.0
    )
    e = col.features.extrudeFeatures.createInput(sk.profiles.item(0), New)
    e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(INTO))
    feat = col.features.extrudeFeatures.add(e)
    tools = adsk.core.ObjectCollection.create()
    tools.add(feat.bodies.item(0))
    cin = col.features.combineFeatures.createInput(body, tools)
    cin.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    cin.isKeepToolBodies = False
    col.features.combineFeatures.add(cin)
    sk.isVisible = False

    body = col.bRepBodies.item(0)
    body.name = "ColumnBody"

    # Wire bore — NewBody + Combine so we don't hit other components in DM
    pin = col.constructionPlanes.createInput()
    pin.setByOffset(xy, adsk.core.ValueInput.createByReal(z_bot - 0.05))
    pl = col.constructionPlanes.add(pin)
    sk = col.sketches.add(pl)
    sk.name = "WireBore"
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), ID / 2.0
    )
    e = col.features.extrudeFeatures.createInput(sk.profiles.item(0), New)
    e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(BELOW + INTO + 0.2))
    feat = col.features.extrudeFeatures.add(e)
    tools = adsk.core.ObjectCollection.create()
    tools.add(feat.bodies.item(0))
    cin = col.features.combineFeatures.createInput(body, tools)
    cin.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    cin.isKeepToolBodies = False
    col.features.combineFeatures.add(cin)
    sk.isVisible = False

    bb = body.boundingBox
    print(
        "Column rebuilt Zmm",
        round(bb.minPoint.z * 10, 2),
        "..",
        round(bb.maxPoint.z * 10, 2),
        "vol",
        round(body.volume, 3),
    )
