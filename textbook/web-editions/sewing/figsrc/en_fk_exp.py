# fk_exp (Fig. 17-3c): exploded view re-rendered from the English 3D lab (src/en/labs/model-flatknit.html, #capture mode)
import subprocess, json, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
state = {"mode": "explode", "ex": 1, "view": "iso", "cam": [-0.65, 0.42, 3000], "target": [0, 60, 0]}
labels = {"Yarn carrier": [-40, -120], "Carrier rail": [120, -30], "Carriage (cam plate)": [200, -170],
          "Stitch cam (loop length)": [330, 110], "Raising cam": [340, 40], "Take-down rollers": [-120, 25]}
subprocess.run(['node', 'figsrc/en17/shot3d.js', 'en', json.dumps(state), 'img/en/fk_exp.png', json.dumps(labels)], check=True, timeout=290)
