from sparc_simulator import SPARCSimulator

if __name__ == "__main__":
    simulator = SPARCSimulator()
    simulator.load_program_from_file("asm/test.s")
    simulator.execute("main", True)