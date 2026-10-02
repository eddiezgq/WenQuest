# ps_iso (Fig. 17-3b): oblique X-ray view re-rendered from the English 3D lab (#capture mode)
import subprocess, json, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
state = {"mode": "xray", "ex": 0, "view": "iso", "xc": 0}
labels = {"Fabric": [300, 170]}  # moved so it no longer collides with "Stitch cam (loop length)"
subprocess.run(['node', 'figsrc/en17/shot3d.js', 'en', json.dumps(state), 'img/en/ps_iso.png', json.dumps(labels)], check=True, timeout=290)
