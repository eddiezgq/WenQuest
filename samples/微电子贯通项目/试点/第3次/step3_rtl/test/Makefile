# 贯通项目步骤三：cocotb 测试（Icarus Verilog）。运行：make（或 wqlab test 目录）
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(CURDIR)/../src
VERILOG_SOURCES += $(SRC_DIR)/project.v $(SRC_DIR)/pwm_gen.v $(SRC_DIR)/quad_dec.v
# cocotb 2.x 的变量名；1.x 用后两个
COCOTB_TOPLEVEL = tt_um_wenquest_motor
COCOTB_TEST_MODULES = test_motor
TOPLEVEL = tt_um_wenquest_motor
MODULE = test_motor
include $(shell cocotb-config --makefiles)/Makefile.sim
