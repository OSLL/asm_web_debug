import subprocess

res = subprocess.run(["x86_64-linux-gnu-as", "-g", "../demos/demo_helloworld.x86_64.s3",
	       "-o", "../demos/demo_helloworld.x86_64.o"], capture_output = True)

print(res.stdout)
print(res.stderr)
print(res.returncode)
