import argparse

def run_tortoise():
    pass

def run_sovits():
    pass

def run_coqui():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)

    args = parser.parse_args()

    if args.model == "tortoise":
        run_tortoise()
    elif args.model == "sovits":
        run_sovits()
    elif args.model == "coqui":
        run_coqui()
