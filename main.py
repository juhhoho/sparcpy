from sparc_simulator import SPARCSimulator

if __name__ == "__main__":
    simulator = SPARCSimulator()
    simulator.load_program_from_file("")
    simulator.execute("main")
