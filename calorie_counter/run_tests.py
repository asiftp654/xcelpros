#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

print("Running tests...")
test_dir = Path(__file__).parent / "app" / "tests"
result = subprocess.run([sys.executable, "-m", "pytest", str(test_dir), "-v"])
print("Done!" if result.returncode == 0 else "Failed!")