v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {第 1 章参考解：CMOS 反相器（SKY130，Wp/Wn ≈ r）} -220 -230 0 0 0.4 0.4 {}
C {sky130_fd_pr/pfet_01v8.sym} 0 -100 0 0 {name=M2
L=0.15
W=0.97
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'"
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'"
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 0 100 0 0 {name=M1
L=0.15
W=0.42
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'"
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'"
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {lab_pin.sym} 20 -130 0 0 {name=l1 lab=VDD}
C {lab_pin.sym} 20 -100 0 0 {name=l2 lab=VDD}
C {lab_pin.sym} 20 -70 0 0 {name=l3 lab=OUT}
C {lab_pin.sym} -20 -100 0 1 {name=l4 lab=IN}
C {lab_pin.sym} 20 70 0 0 {name=l5 lab=OUT}
C {lab_pin.sym} 20 100 0 0 {name=l6 lab=VSS}
C {lab_pin.sym} 20 130 0 0 {name=l7 lab=VSS}
C {lab_pin.sym} -20 100 0 1 {name=l8 lab=IN}
C {ipin.sym} -160 0 0 0 {name=p1 lab=IN}
C {opin.sym} 160 0 0 0 {name=p2 lab=OUT}
C {iopin.sym} -160 -170 0 0 {name=p3 lab=VDD}
C {iopin.sym} -160 170 0 0 {name=p4 lab=VSS}
