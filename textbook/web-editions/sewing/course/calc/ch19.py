"""Ch19 numbers for the course pack. Uses the book's own model figsrc/ch19_calc.py (imported, main() not run)."""
import sys, os, copy, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'figsrc'))
import ch19_calc as M

RPM = 2 * math.pi / 60
R = {}
r = M.REQ['LS']
for ms in ('250', '400', '550'):
    s = M.spindle_need(r, M.item('D-MOT-PMSM', ms))
    R[f'LS_{ms}'] = dict(T_acc=s['T_acc'], T_rms=s['T_rms'], ratio=s['ratio'], E_regen=s['E_regen'], alpha=s['alpha'])
cfg = M.configure('LS'); R['LS_total'] = cfg['total']; R['LS_Ic'] = cfg['spindle']['Ic']; R['LS_Ip'] = cfg['spindle']['Ip']
R['LS_psu_need'] = cfg['psu24']['need']; R['LS_psu'] = cfg['psu24']['size']
R['t_acc_min_2.5'] = 6e-4 * 5000 * RPM / (2.5 - 0.15)
R['M15_trim_max'] = 20 / (6 * 0.0069)
R['OL_total'] = M.configure('OL')['total']
r7 = copy.deepcopy(M.REQ['OL']); r7['n_max'] = 7000
c7 = M.configure('OL', r7); R['OL7000'] = (c7['spindle']['mot'], c7['spindle']['drv'], c7['total'], c7['spindle']['E_regen'])
s, C = M.spindle_check(r7, M.item('D-MOT-PMSM', '400'), M.item('D-DRV-SERVO', '3A')); R['OL7000_400_regen'] = s['E_regen']
# encoder
R['counts_s_5000'] = 5000 / 60 * 10000; R['us_per_0.1deg_300'] = 0.1 / (300 * 6) * 1e6; R['us_per_0.1deg_5000'] = 0.1 / (5000 * 6) * 1e6
R['HIL_deg_50us'] = 5000 / 60 * 360 * 50e-6; R['HIL_counts_50us'] = 5000 / 60 * 10000 * 50e-6
# exercises
J = 4e-4 + 1e-4; w = 5000 * RPM
R['ex1_T'] = J * w / 0.12 + 0.15; R['ex1_ratio'] = 4; R['ex1_E'] = 0.7 * 0.5 * J * w**2
R['ex2_on'] = 6 * 300 * 0.011; R['ex2_off'] = 6 * 300 * 0.007; R['ex2_nmax'] = 20 / (6 * 0.011)
R['ex3_counts'] = 7000 / 60 * 10000; R['ex3_us'] = 0.1 / (7000 * 6) * 1e6; R['ex3_deg_per_ms'] = 7000 * 6 / 1000
# quiz / exam / assignment variants
R['q_trim_angle_500_M15'] = 6 * 500 * 0.0069                 # 500 r/min, M15 pull-in
R['q_regen_6000'] = 0.7 * 0.5 * (3e-4 + 1e-4) * (6000 * RPM)**2  # OL default with 400 W
R['q_cnt_to_deg'] = 3750 * 9 / 25                              # count 3750 -> 0.1 deg units
R['q_Tacc_J7'] = (7e-4) * (4500 * RPM) / 0.15 + 0.15           # J_total 7e-4, 4500 r/min, 0.15 s
R['ex_bt_angle_L30_1500'] = 6 * 1500 * 0.011
R['ex_psu'] = 1.2 * (8 + 30.0 + 72)
# assignment: lockstitch variant: J_load 6e-4, n_max 4500, t_acc 0.12, starts 30/min
ra = copy.deepcopy(M.REQ['LS']); ra['n_max'] = 4500; ra['t_acc'] = 0.12; ra['J_load'] = 6e-4
for ms in ('250', '400', '550', '750'):
    for ds in ('1A5', '3A', '5A'):
        try:
            s, C = M.spindle_check(ra, M.item('D-MOT-PMSM', ms), M.item('D-DRV-SERVO', ds))
        except StopIteration:
            continue
        R[f'as_{ms}_{ds}'] = dict(T_acc=round(s['T_acc'], 3), T_rms=round(s['T_rms'], 3), ratio=round(s['ratio'], 2), Ic=round(s['Ic'], 2), Ip=round(s['Ip'], 2), E=round(s['E_regen'], 1), ok=[x['ok'] for x in C])
ca = M.configure('LS', ra); R['as_choice'] = (ca['spindle']['mot'], ca['spindle']['drv'], ca['total'])
R['as_trim_n_M15_L30'] = (20 / (6 * 0.0069), 20 / (6 * 0.011))
R['drv_sizes'] = [(d['size'], d['cont_current_A'], d['peak_current_A'], d['brake_energy_J'], d['price']) for d in M.LIB['D-DRV-SERVO']['sizes']]
R['mot_sizes'] = [(m['size'], m['max_speed_rpm'], m['rated_torque_Nm'], m['peak_torque_Nm'], m['rotor_inertia_kgm2'], m['kt_NmA'], m['price']) for m in M.LIB['D-MOT-PMSM']['sizes']]
R['sol_sizes'] = [(s['size'], s['stroke_mm'], s['force_at_stroke_N'], s['t_on_ms'], s['t_off_ms'], s['coil_R_ohm'], s['hold_A'], s['price']) for s in M.LIB['D-SOL-PUSH']['sizes']]

if __name__ == '__main__':
    for k, v in R.items():
        print(k, v if not isinstance(v, float) else round(v, 4))
