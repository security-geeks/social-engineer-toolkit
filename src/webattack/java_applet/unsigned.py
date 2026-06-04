#!/usr/bin/python
#
# simple jar file
#
import subprocess
import os
import shutil

for artifact in ("Java_Update.jar", "Java.class"):
    try:
        os.remove(artifact)
    except FileNotFoundError:
        pass

subprocess.Popen(["javac", "Java.java"]).wait()
subprocess.Popen(["jar", "cvf", "Java_Update.jar", "Java.class"]).wait()
subprocess.Popen(["jar", "ufm", "Java_Update.jar", "manifest.mf"]).wait()
shutil.copyfile(
    "Java_Update.jar",
    os.path.join("..", "..", "html", "unsigned", "unsigned.jar"),
)
print("[*] Jar file exported as Java_Update.jar")
