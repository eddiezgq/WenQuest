# Plant manifest: bring your shop in

> Hand in one Excel file: company, workstations, where each machine stands, operations, shifts, targets. The digital factory, ERPNext and the 3D shop are all built from it.

## Editing on the web (process engineers, plant managers)

At the top of [Design & process](/work/engineer) is “Plant manifest (Excel)”:

1. **Download the manifest in use**: get the Excel of the manifest the plant runs on now (the same format as the template generated on the command line below);
2. **Edit it in Excel**: add a product, change BOM quantities, routing minutes, prices…;
3. **Upload the edited manifest**: the platform checks it on the spot and names the sheet and row of any error; if it passes it lists what changed against the manifest in use (items, BOMs, operations and products added / removed / changed) and saves it as a “pending manifest”.

A pending manifest is not in effect yet: for now the implementation team downloads its yaml and takes it live with step 3 below; one-click go-live from the web (creating new items in ERPNext too, keeping the old manifest for rollback) comes in the next phase.

## Three steps

```anim
name: terminal
title: Your computer
$ python -m factory.plant template plant-manifest.xlsx
Template created: plant-manifest.xlsx
$ python -m factory.plant import plant-manifest.xlsx plant.yaml
The plant manifest has 2 errors:
  - Machines sheet row 6 “x / y / width / depth”: fill in all four
  - Operations sheet row 3 “Machines”: no such machine: lathe-3
$ python -m factory.plant import plant-manifest.xlsx plant.yaml
Imported: plant-manifest.xlsx → plant.yaml (8 workstations, 13 machines, 12 operations)
$ python -m factory.plant check plant.yaml
Manifest OK: Example Sewing Machine Plant, 8 workstations, 13 machines, 12 operations
```

1. **Create the template**: run it in the repository's `factory/` directory. The template is already filled in for the demo plant (WenQuest Gearbox) as an example;
2. **Edit it into your shop**: if something is wrong, the import tells you which sheet, row and column;
3. **Hand it to us to go live**: the manifest goes into the repository's `factory/plants/` and is released with the factory image; in the server's `.env` write
   `WQ_PLANT_FILE=/app/plants/your-manifest.yaml`, then run `deploy/update.sh` (no arguments, restarts the current version).
   Without `WQ_PLANT_FILE` you get the demo plant.

The plant name and counts in the terminal come from the example sewing machine plant (`factory/plants/example-sewing.yaml` in the repository); yours follow your manifest.

## What goes in each sheet

| Sheet | Each row is | Key points |
| --- | --- | --- |
| Plant | One item | Company name, abbreviation, country (in English), currency, time zone; raw material store and finished goods store (machine IDs); shop length, width, aisles; shifts, working days, overtime limit; three target metrics |
| Workstations | A group of similar machines | Name (the ERPNext workstation name), count, hourly depreciation / labor / energy rates |
| Machines | One machine | ID, area, Chinese and English names, workstation; center x, y and width, depth (meters, origin at the shop's lower-left corner); board order; for logistics carts the docking points |
| Operations | One operation | Operation name (matching the routing), workstation, machines (IDs, comma-separated), stage, whether it is an inspection |
| Suppliers, customers | One company | Optional |
| Items (version 2; the six sheets from here on may be left out as a group) | One item | ID, name, category (raw material / purchased / made / subassembly / finished), unit, unit price, supplier, parts library ID |
| Routings | One operation | Routing name (consecutive rows for one routing), operation, minutes per piece |
| BOM | One component | Parent (consecutive rows for one parent), parent's routing, component, quantity; may be multi-level |
| Finished goods | One finished item that can be ordered | Item ID, selling price |
| Stock | One item | Opening stock, safety stock, order on the board's “key materials” |
| Characteristics | One characteristic | Measured on which item at which operation; name, unit, nominal, upper and lower limits, scatter σ (example values for simulation) |
| Engineer to order (optional) | One item | Job number prefix, risk reserve (%), markup (%), design rate (per hour), quote validity days; if left out these are “unknown” in estimates and no quote can be made |
| Milestone billing (optional) | One milestone | Code, name, share (%, all milestones add up to 100), when to invoice (order confirmed / design released / shipped / accepted) |

Leave cells you do not know empty; do not write 0 instead. Simulation parameters (changeover, tool wear, etc.) use defaults when empty.
With the six product sheets filled in (manifest version 2), the plant can take orders as soon as it starts: MRP explodes the multi-level BOM, and characteristics produce measurements and inspection records at their operation;
without them, products come in as before from design via “Convert to production item”. The robot plant of WenQuest Digital Industrial Park is a version 2 manifest (`factory/plants/wenquest-robot.yaml`).

## How an enterprise plant differs from the demo plant

With your own manifest (`demo_data: false` in it), the workbench keeps only the general parts: orders and planning, shop floor, quality, production cost,
Plant Insight Hub, 3D shop. Teaching content written only for the gearbox demo plant (the seven domains such as customers and service, labs and tasks, scenario director, virtual PLC) is not shown.

## Your manifest right now

```live
kind: plant
```

The 3D shop is drawn from the layout in the manifest:

```goto
tour: open-3d
label: Open the 3D shop and look at your shop
```

```ask
q: How should operation names in the plant manifest be written so they match the routing?
```
