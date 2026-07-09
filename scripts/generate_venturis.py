# --- VenturiFlowLab Batch Venturi Generator ---
import FreeCAD as App
import Part
import csv
import os
import math

# ---------- CONFIG ----------
csv_path = r"C:\Users\Aakash\Desktop\Venturi Papers\venturi_samples.csv"
output_dir = r"C:\Users\Aakash\Desktop\Venturi Papers\Generated"
doc_name = "VenturiBatch"

# ---------- SETUP ----------
if not os.path.isfile(csv_path):
    raise FileNotFoundError(f"CSV not found at: {csv_path}")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

doc = App.newDocument(doc_name)


def make_venturi(inlet_d, throat_d, outlet_d, conv_angle_deg, div_angle_deg, throat_length, name):
    """
    Builds an axisymmetric Venturi as a revolved profile.
    All diameters/lengths in mm, angles in degrees.
    Includes a straight constant-diameter throat section (throat_length),
    instead of the cones meeting at a sharp point.
    """
    r_in = inlet_d / 2.0
    r_th = throat_d / 2.0
    r_out = outlet_d / 2.0

    conv_angle = math.radians(conv_angle_deg)
    div_angle = math.radians(div_angle_deg)

    len_conv = (r_in - r_th) / math.tan(conv_angle)
    len_div = (r_out - r_th) / math.tan(div_angle)

    # Profile points: inlet -> start of throat -> end of throat -> outlet
    p0 = App.Vector(0, r_in, 0)
    p1 = App.Vector(len_conv, r_th, 0)
    p1b = App.Vector(len_conv + throat_length, r_th, 0)
    p2 = App.Vector(len_conv + throat_length + len_div, r_out, 0)

    line1 = Part.LineSegment(p0, p1)          # converging cone
    line_throat = Part.LineSegment(p1, p1b)   # straight throat section
    line2 = Part.LineSegment(p1b, p2)         # diverging cone

    axis_p0 = App.Vector(0, 0, 0)
    axis_p1 = App.Vector(len_conv + throat_length + len_div, 0, 0)

    close1 = Part.LineSegment(p2, axis_p1)
    close2 = Part.LineSegment(axis_p1, axis_p0)
    close3 = Part.LineSegment(axis_p0, p0)

    wire = Part.Wire([
        line1.toShape(),
        line_throat.toShape(),
        line2.toShape(),
        close1.toShape(),
        close2.toShape(),
        close3.toShape()
    ])
    face = Part.Face(wire)

    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 360)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = solid
    return obj


# ---------- READ CSV & GENERATE ----------
with open(csv_path, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows from CSV")
if rows:
    print("Detected columns:", list(rows[0].keys()))

for i, row in enumerate(rows):
    try:
        row_id = row['ID']
        inlet_d = float(row['Inlet Diameter'])
        outlet_d = float(row['Outlet Diameter'])
        throat_d = float(row['Throat Diameter'])
        conv_angle = float(row['Converging Angle'])
        div_angle = float(row['Diverging Angle'])
        throat_length = float(row['Throat Length'])
        name = f"Venturi_{row_id}"

        obj = make_venturi(inlet_d, throat_d, outlet_d, conv_angle, div_angle, throat_length, name)
        doc.recompute()

        step_path = os.path.join(output_dir, f"{name}.step")
        obj.Shape.exportStep(step_path)
        print(f"[{i+1}/{len(rows)}] Generated: {name} -> {step_path}")

    except KeyError as e:
        print(f"Row {i+1} missing column: {e}. Skipping.")
    except ZeroDivisionError:
        print(f"Row {i+1} has zero-degree angle, can't build geometry. Skipping.")
    except Exception as e:
        print(f"Row {i+1} failed: {e}. Skipping.")

doc.recompute()
App.Gui.activeDocument().activeView().viewAxonometric()
App.Gui.SendMsgToActiveView("ViewFit")

print("Batch generation complete.")

