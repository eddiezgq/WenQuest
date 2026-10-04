load nand2 -silent
snap internal
# gate strips (metal1): A over N1/P1 gates, B over N2/P2 gates
box -29 43 29 648
paint metal1
box 673 43 731 648
paint metal1
# X: N1.S -> N2.D
box 21 -73 681 -27
paint metal1
# VSS rail over the NMOS guard rings + mcon to each ring
box -175 -197 877 -139
paint metal1
box -145 -185 -111 -151
paint viali
box 557 -185 591 -151
paint viali
# N1.D -> VSS
box -67 -139 -21 -73
paint metal1
# VDD rail over PMOS guard rings + mcon
box -175 949 877 1007
paint metal1
box -145 961 -111 995
paint viali
box 557 961 591 995
paint viali
# P1.D, P2.D -> VDD
box -67 883 -21 949
paint metal1
box 635 883 681 949
paint metal1
# OUT: via1 on N2.S, P2.S, P1.S, joined by metal2
box 720 -69 772 7
paint metal1
box 720 -57 772 -5
paint via1
box 720 688 772 764
paint metal1
box 720 700 772 752
paint via1
box 18 688 70 764
paint metal1
box 18 700 70 752
paint via1
box 720 -69 772 764
paint metal2
box 18 688 772 764
paint metal2
# labels / ports
box 0 300 0 300
label A c metal1
port make
box 702 300 702 300
label B c metal1
port make
box 746 300 746 300
label OUT c metal2
port make
box 300 978 300 978
label VDD c metal1
port make
box 300 -168 300 -168
label VSS c metal1
port make
select top cell
drc style drc(full)
drc check
drc catchup
puts "DRC [drc list count total]"
foreach {why boxes} [drc listall why] { puts "WHY $why ([llength $boxes])" }
save nand2
quit -noprompt
