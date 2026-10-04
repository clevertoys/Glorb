# Fusion: BaseTub (floor + short lip + stays) and BaseTop (skirt walls + shell + column socket).
# Top slides down over the tub lip. Units: cm.
# Entry: build_base() — do not name this run() (Fusion MCP auto-invokes run).

import adsk.core
import adsk.fusion


def build_base():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError("No design")
    root = design.rootComponent

    # --- dims cm ---
    # Outer OD of assembled base = BaseTop exterior
    D = 17.0  # 170 mm — room for stays + lip + skirt wall
    WALL = 0.50  # top skirt wall
    LIP_T = 0.25  # tub short register wall
    SLIP = 0.04  # diametral clearance top-ID vs tub-lip-OD
    FLOOR = 0.20
    CLEAR = 4.445  # bay height (floor top → shell underside)
    SHELL = 0.50
    LIP_H = 1.00  # short tub lip the skirt slides over

    # Top ID / tub lip OD
    TOP_ID = D - 2 * WALL  # 16.0
    LIP_OD = TOP_ID - SLIP  # 15.96
    BAY_ID = LIP_OD - 2 * LIP_T  # clear diameter inside lip
    BAY_R = BAY_ID / 2.0

    COL_OD = 2.80
    COL_ID = 1.60
    SOCKET_H = 1.20
    SOCKET_OD = COL_OD + 0.60

    JACK_D = 1.20
    # Above lip so skirt opens directly into bay (lip top = FLOOR+LIP_H)
    JACK_Z = FLOOR + 2.00  # 20 mm above floor deck / 22 mm from tub bottom

    # Orientation: −Y = front (power switch), +Y = back (DC jack)
    # DaierTek KCD1-5-101 round rocker (Amazon B07S1MV462): snap-in Ø20 mm panel hole
    SW_HOLE = 2.02  # 20.2 mm — slight print clearance on 20 mm spec
    SW_CB_D = 2.40  # underside counterbore so snap lips see ~2 mm panel
    SW_PANEL_T = 0.20  # remaining shell thickness at switch
    SW_X, SW_Y = 0.0, -5.0  # front on lid

    BATT = (7.2, 5.7, 3.9)
    ESP = (5.5, 3.0, 1.5)
    BUCK = (1.75, 1.23, 0.43)

    STAY_T = 0.15
    STAY_H = 1.00
    STAY_MARGIN = 0.30  # keep stay outer inside bay

    # World Z: shell top seats on Column bottom
    Z_COL_BOT = None
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        if occ.component.name != "Column":
            continue
        if occ.component.bRepBodies.count == 0:
            continue
        bb = occ.component.bRepBodies.item(0).boundingBox
        Z_COL_BOT = bb.minPoint.z + occ.transform.translation.z
        break
    if Z_COL_BOT is None:
        Z_COL_BOT = -15.24 - 10.0
    z_tub0 = Z_COL_BOT - SHELL - CLEAR - FLOOR

    def delete_named(names):
        i = root.occurrences.count - 1
        while i >= 0:
            occ = root.occurrences.item(i)
            if occ.component.name in names:
                occ.deleteMe()
            i -= 1

    delete_named(["BaseTub", "BaseTop"])

    def new_comp(name, world_z):
        tm = adsk.core.Matrix3D.create()
        tm.translation = adsk.core.Vector3D.create(0, 0, world_z)
        occ = root.occurrences.addNewComponent(tm)
        occ.component.name = name
        return occ

    def clear_comp(comp):
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

    def combine_cut(comp, target, cutter_body):
        tools = adsk.core.ObjectCollection.create()
        tools.add(cutter_body)
        cin = comp.features.combineFeatures.createInput(target, tools)
        cin.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        cin.isKeepToolBodies = False
        comp.features.combineFeatures.add(cin)

    def combine_join(comp, target, tool_body):
        tools = adsk.core.ObjectCollection.create()
        tools.add(tool_body)
        cin = comp.features.combineFeatures.createInput(target, tools)
        cin.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        cin.isKeepToolBodies = False
        comp.features.combineFeatures.add(cin)

    New = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    Cut = adsk.fusion.FeatureOperations.CutFeatureOperation

    def extrude_circle(comp, plane, name, radius, height, op, z_off=None, target=None):
        if z_off is not None:
            pin = comp.constructionPlanes.createInput()
            pin.setByOffset(plane, adsk.core.ValueInput.createByReal(z_off))
            pl = comp.constructionPlanes.add(pin)
            pl.name = name + "Pl"
            sk_plane = pl
        else:
            sk_plane = plane
        sk = comp.sketches.add(sk_plane)
        sk.name = name
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), radius
        )
        prof = sk.profiles.item(0)
        ext = comp.features.extrudeFeatures
        if op == Cut and target is not None:
            e = ext.createInput(prof, New)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            feat = ext.add(e)
            combine_cut(comp, target, feat.bodies.item(0))
        elif op == adsk.fusion.FeatureOperations.JoinFeatureOperation and target is not None:
            e = ext.createInput(prof, New)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            feat = ext.add(e)
            combine_join(comp, target, feat.bodies.item(0))
        else:
            e = ext.createInput(prof, op)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            feat = ext.add(e)
        sk.isVisible = False
        return feat

    def extrude_rect(comp, plane, name, cx, cy, sx, sy, height, op, z_off=0.0, target=None):
        pin = comp.constructionPlanes.createInput()
        pin.setByOffset(plane, adsk.core.ValueInput.createByReal(z_off))
        pl = comp.constructionPlanes.add(pin)
        pl.name = name + "Pl"
        sk = comp.sketches.add(pl)
        sk.name = name
        lines = sk.sketchCurves.sketchLines
        hx, hy = sx / 2.0, sy / 2.0
        pts = [
            adsk.core.Point3D.create(cx - hx, cy - hy, 0),
            adsk.core.Point3D.create(cx + hx, cy - hy, 0),
            adsk.core.Point3D.create(cx + hx, cy + hy, 0),
            adsk.core.Point3D.create(cx - hx, cy + hy, 0),
        ]
        for i in range(4):
            lines.addByTwoPoints(pts[i], pts[(i + 1) % 4])
        prof = sk.profiles.item(0)
        ext = comp.features.extrudeFeatures
        if op == Cut and target is not None:
            e = ext.createInput(prof, New)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            feat = ext.add(e)
            combine_cut(comp, target, feat.bodies.item(0))
        elif op == adsk.fusion.FeatureOperations.JoinFeatureOperation and target is not None:
            e = ext.createInput(prof, New)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            feat = ext.add(e)
            combine_join(comp, target, feat.bodies.item(0))
        else:
            e = ext.createInput(prof, op)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            feat = ext.add(e)
        sk.isVisible = False
        return feat

    def wall_port(comp, body, name, axis, plane_pos, outward_sign, d_ref, sketch_fn, depth):
        """Cut a port through a sidewall. axis='x' → YZ plane; axis='y' → XZ plane."""
        pin = comp.constructionPlanes.createInput()
        parent = comp.yZConstructionPlane if axis == "x" else comp.xZConstructionPlane
        pin.setByOffset(parent, adsk.core.ValueInput.createByReal(plane_pos))
        pl = comp.constructionPlanes.add(pin)
        pl.name = name + "Pl"
        sk = comp.sketches.add(pl)
        sk.name = name
        sketch_fn(sk)
        prof = sk.profiles.item(0)
        last_err = None
        for neg in (False, True):
            feat = None
            try:
                e = comp.features.extrudeFeatures.createInput(prof, New)
                e.setDistanceExtent(neg, adsk.core.ValueInput.createByReal(depth))
                feat = comp.features.extrudeFeatures.add(e)
                cutter = feat.bodies.item(0)
                bb = cutter.boundingBox
                if axis == "x":
                    a0, a1 = bb.minPoint.x, bb.maxPoint.x
                else:
                    a0, a1 = bb.minPoint.y, bb.maxPoint.y
                reaches_out = (outward_sign > 0 and a1 >= d_ref / 2.0 - 0.05) or (
                    outward_sign < 0 and a0 <= -d_ref / 2.0 + 0.05
                )
                if not reaches_out:
                    cutter.deleteMe()
                    continue
                combine_cut(comp, body, cutter)
                sk.isVisible = False
                return
            except Exception as ex:
                last_err = ex
                try:
                    if feat is not None:
                        for bi in range(feat.bodies.count - 1, -1, -1):
                            feat.bodies.item(bi).deleteMe()
                except Exception:
                    pass
        raise RuntimeError("%s failed: %s" % (name, last_err))

    # ========== BaseTub: floor + short lip + stays ==========
    occ_tub = new_comp("BaseTub", z_tub0)
    tub = occ_tub.component
    clear_comp(tub)
    xy = tub.xYConstructionPlane

    # Floor disk — full OD, flush with BaseTop outer skirt (assembly stop)
    extrude_circle(tub, xy, "Floor", D / 2.0, FLOOR, New)
    tub_body = tub.bRepBodies.item(0)

    # Short lip (register) — top skirt slides over this; sits on floor
    extrude_circle(
        tub, xy, "Lip", LIP_OD / 2.0, LIP_H,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        z_off=FLOOR, target=tub_body,
    )
    extrude_circle(
        tub, xy, "LipCavity", BAY_ID / 2.0, LIP_H + 0.05, Cut, z_off=FLOOR, target=tub_body,
    )

    # Stay centers — packed inside bay (R ≈ BAY_R)
    # Front = −Y (switch). Battery toward front, ESP −X (USB), buck near jack at back (+Y)
    bx, by = -0.5, -1.8
    ex, ey = -2.8, 2.8
    ux, uy = 0.3, 4.2

    def stay_ok(cx, cy, sx, sy):
        hx, hy = (sx + 2 * STAY_T) / 2.0, (sy + 2 * STAY_T) / 2.0
        for px, py in (
            (cx - hx, cy - hy),
            (cx + hx, cy - hy),
            (cx + hx, cy + hy),
            (cx - hx, cy + hy),
        ):
            if (px * px + py * py) ** 0.5 > BAY_R - STAY_MARGIN:
                raise RuntimeError(
                    "Stay out of bay: center=(%.2f,%.2f) corner=(%.2f,%.2f) bay_r=%.2f"
                    % (cx, cy, px, py, BAY_R)
                )

    def stay_box(name, cx, cy, sx, sy):
        stay_ok(cx, cy, sx, sy)
        extrude_rect(
            tub, xy, name + "Out", cx, cy, sx + 2 * STAY_T, sy + 2 * STAY_T, STAY_H,
            adsk.fusion.FeatureOperations.JoinFeatureOperation, z_off=FLOOR, target=tub_body,
        )
        extrude_rect(
            tub, xy, name + "In", cx, cy, sx, sy, STAY_H + 0.05, Cut, z_off=FLOOR, target=tub_body,
        )

    stay_box("BattStay", bx, by, BATT[0] + 0.2, BATT[1] + 0.2)
    stay_box("EspStay", ex, ey, ESP[0] + 0.2, ESP[1] + 0.2)
    stay_box("BuckStay", ux, uy, BUCK[0] + 0.3, BUCK[1] + 0.3)

    # Short center rib (does not reach lip)
    rib_len = min(BAY_ID - 1.0, 10.0)
    extrude_rect(
        tub, xy, "RibY", 0.0, 0.0, STAY_T, rib_len, STAY_H,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, z_off=FLOOR, target=tub_body,
    )
    extrude_rect(
        tub, xy, "RibClearBatt", bx, by, BATT[0], BATT[1], STAY_H + 0.1, Cut,
        z_off=FLOOR, target=tub_body,
    )
    extrude_rect(
        tub, xy, "RibClearEsp", ex, ey, ESP[0], ESP[1], STAY_H + 0.1, Cut,
        z_off=FLOOR, target=tub_body,
    )

    # ========== BaseTop: skirt walls + shell + column socket ==========
    # Origin at floor upper surface so skirt hangs from lid down to floor
    occ_top = new_comp("BaseTop", z_tub0 + FLOOR)
    top = occ_top.component
    clear_comp(top)
    xy2 = top.xYConstructionPlane

    # Outer blank: full skirt + shell
    h_top = CLEAR + SHELL
    extrude_circle(top, xy2, "SkirtBlank", D / 2.0, h_top, New)
    top_body = top.bRepBodies.item(0)

    # Hollow bay (leave shell deck at top)
    extrude_circle(
        top, xy2, "SkirtCavity", TOP_ID / 2.0, CLEAR + 0.05, Cut, z_off=0.0, target=top_body,
    )

    # Column socket boss on shell upper face
    extrude_circle(
        top, xy2, "SocketBoss", SOCKET_OD / 2.0, SOCKET_H,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        z_off=h_top, target=top_body,
    )

    # Step is already: boss only above shell (boss joined on top of full-D blank's top face)
    # Carve: nothing more needed — boss is smaller and joined on top.

    # Column bore in boss only
    extrude_circle(
        top, xy2, "ColBore", (COL_OD + 0.04) / 2.0, SOCKET_H + 0.15, Cut,
        z_off=h_top - 0.05, target=top_body,
    )
    # Wire bore through shell into bay
    extrude_circle(
        top, xy2, "WireBore", (COL_ID - 0.1) / 2.0, SHELL + SOCKET_H + 0.3, Cut,
        z_off=CLEAR - 0.05, target=top_body,
    )
    # Aux wire pass through shell
    pinw = top.constructionPlanes.createInput()
    pinw.setByOffset(xy2, adsk.core.ValueInput.createByReal(CLEAR - 0.05))
    plw = top.constructionPlanes.add(pinw)
    skw = top.sketches.add(plw)
    skw.name = "WirePassOff"
    skw.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(1.50, 0.0, 0.0), 0.40
    )
    ew = top.features.extrudeFeatures.createInput(skw.profiles.item(0), New)
    ew.setDistanceExtent(False, adsk.core.ValueInput.createByReal(SHELL + 0.2))
    wfeat = top.features.extrudeFeatures.add(ew)
    combine_cut(top, top_body, wfeat.bodies.item(0))
    skw.isVisible = False

    # Power switch (KCD1-5-101): Ø20.2 through + underside CB → ~2 mm snap land
    def shell_hole(name, cx, cy, radius, height, z0):
        pin = top.constructionPlanes.createInput()
        pin.setByOffset(xy2, adsk.core.ValueInput.createByReal(z0))
        pl = top.constructionPlanes.add(pin)
        pl.name = name + "Pl"
        sk = top.sketches.add(pl)
        sk.name = name
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx, cy, 0.0), radius
        )
        e = top.features.extrudeFeatures.createInput(sk.profiles.item(0), New)
        e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
        feat = top.features.extrudeFeatures.add(e)
        combine_cut(top, top_body, feat.bodies.item(0))
        sk.isVisible = False

    shell_hole("SwHole", SW_X, SW_Y, SW_HOLE / 2.0, SHELL + 0.2, CLEAR - 0.05)
    shell_hole(
        "SwCbore", SW_X, SW_Y, SW_CB_D / 2.0, SHELL - SW_PANEL_T + 0.05, CLEAR - 0.05
    )

    # Ports: jack at back (+Y) through skirt into bay; USB on −X side
    # Sketch on OUTER face and cut inward — more reliable than inner-face outward
    jack_z_local = JACK_Z - FLOOR  # 20 mm above floor top

    def jack_sk(sk):
        # XZ plane: sketch x→X, sketch y→Z
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0.0, jack_z_local, 0.0), JACK_D / 2.0
        )

    # Probe both sketch-Y signs in case plane Y maps opposite model Z
    jack_done = False
    last_jack_err = None
    for z_sign in (1.0, -1.0):
        def jack_sk_try(sk, zs=z_sign):
            sk.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(0.0, zs * jack_z_local, 0.0), JACK_D / 2.0
            )

        pin = top.constructionPlanes.createInput()
        pin.setByOffset(top.xZConstructionPlane, adsk.core.ValueInput.createByReal(D / 2.0 - 0.01))
        pl = top.constructionPlanes.add(pin)
        pl.name = "JackHolePl"
        sk = top.sketches.add(pl)
        sk.name = "JackHole"
        jack_sk_try(sk)
        prof = sk.profiles.item(0)
        for neg in (False, True):
            feat = None
            try:
                e = top.features.extrudeFeatures.createInput(prof, New)
                e.setDistanceExtent(neg, adsk.core.ValueInput.createByReal(WALL + 1.0))
                feat = top.features.extrudeFeatures.add(e)
                cutter = feat.bodies.item(0)
                bb = cutter.boundingBox
                # Must sit in the skirt band and at positive local Z in the bay range
                y0, y1 = bb.minPoint.y, bb.maxPoint.y
                z0, z1 = bb.minPoint.z, bb.maxPoint.z
                in_wall = y1 > TOP_ID / 2.0 - 0.1 and y0 < D / 2.0 + 0.2
                in_height = z1 > 0.5 and z0 < CLEAR - 0.5 and (z0 + z1) / 2.0 > 0.5
                if not (in_wall and in_height):
                    cutter.deleteMe()
                    continue
                vol_before = top_body.volume
                combine_cut(top, top_body, cutter)
                if top_body.volume < vol_before - 0.01:
                    jack_done = True
                    sk.isVisible = False
                    print(
                        "jack cut ok z_sign=%.0f neg=%s Zmm=%.1f..%.1f"
                        % (z_sign, neg, z0 * 10, z1 * 10)
                    )
                    break
                # combine didn't remove volume — discard
            except Exception as ex:
                last_jack_err = ex
                try:
                    if feat is not None:
                        for bi in range(feat.bodies.count - 1, -1, -1):
                            feat.bodies.item(bi).deleteMe()
                except Exception:
                    pass
        if jack_done:
            break
        try:
            sk.deleteMe()
        except Exception:
            pass
    if not jack_done:
        raise RuntimeError("JackHole failed to cut skirt: %s" % last_jack_err)

    def usb_sk(sk):
        # YZ plane: sketch x→Y, sketch y→Z
        lines = sk.sketchCurves.sketchLines
        hw, hh = 0.70, 0.50
        cy, cz = ey, 1.0
        pts = [
            adsk.core.Point3D.create(cy - hw, cz - hh, 0),
            adsk.core.Point3D.create(cy + hw, cz - hh, 0),
            adsk.core.Point3D.create(cy + hw, cz + hh, 0),
            adsk.core.Point3D.create(cy - hw, cz + hh, 0),
        ]
        for i in range(4):
            lines.addByTwoPoints(pts[i], pts[(i + 1) % 4])

    wall_port(
        top, top_body, "UsbSlot", "x", -TOP_ID / 2.0, -1, D, usb_sk, WALL + 0.6
    )

    # Hide construction clutter
    for comp in (tub, top):
        for i in range(comp.constructionPlanes.count):
            p = comp.constructionPlanes.item(i)
            try:
                if not p.isOriginPlane:
                    p.isLightBulbOn = False
            except Exception:
                pass
        for i in range(comp.sketches.count):
            comp.sketches.item(i).isVisible = False

    app.activeViewport.fit()
    print("BaseTub + BaseTop OK (slip-over skirt)")
    print(
        "OD=%.0f lip_OD=%.1f bay_ID=%.1f lip_H=%.0f clear=%.1f"
        % (D * 10, LIP_OD * 10, BAY_ID * 10, LIP_H * 10, CLEAR * 10)
    )
    print(
        "tub z0_mm=%.1f  top_z_mm=%.1f  shell_top_mm=%.1f"
        % (z_tub0 * 10, (z_tub0 + FLOOR) * 10, (z_tub0 + FLOOR + CLEAR + SHELL) * 10)
    )
    print(
        "front=−Y switch @ (%.0f,%.0f) mm; back=+Y jack Ø%.0f @ z=%.0f mm (skirt→bay)"
        % (SW_X * 10, SW_Y * 10, JACK_D * 10, JACK_Z * 10)
    )
    print(
        "stays: batt@%.0f,%.0f esp@%.0f,%.0f buck@%.0f,%.0f"
        % (bx * 10, by * 10, ex * 10, ey * 10, ux * 10, uy * 10)
    )
