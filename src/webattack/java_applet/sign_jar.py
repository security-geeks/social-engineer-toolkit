#!/usr/bin/env python
#
# simple jar file
#
import subprocess
import os
import shutil
try:
    print("""
Simply enter in the required fields, easy example below:

Name: FakeCompany
Organization: Fake Company
Organization Name: Fake Company
City: Cleveland
State: Ohio
Country: US
Is this correct: yes

""")
    print("""*** WARNING ***\nIN ORDER FOR THIS TO WORK YOU MUST INSTALL sun-java6-jdk or openjdk-6-jdk, so apt-get install openjdk-6-jdk\n*** WARNING ***""")
    # grab keystore to use later
    subprocess.Popen(
        ["keytool", "-genkey", "-alias", "signapplet2", "-keystore", "mykeystore", "-keypass", "mykeypass", "-storepass", "mystorepass"]).wait()
    # self-sign the applet
    subprocess.Popen(
        ["jarsigner", "-keystore", "mykeystore", "-storepass", "mystorepass", "-keypass", "mykeypass", "-signedjar", "Signed_Update.jar", "Java_Obf.jar", "signapplet2"]).wait()
    # move it into our html directory
    try:
        os.remove(os.path.join("..", "..", "html", "Signed_Update.jar.orig"))
    except FileNotFoundError:
        pass
    shutil.copyfile("Signed_Update.jar", os.path.join("..", "..", "html", "Signed_Update.jar.orig"))
    shutil.copyfile("Java_Obf.jar", os.path.join("..", "..", "html", "unsigned", "unsigned.jar"))
    print("[*] New java applet has been successfully imported into The Social-Engineer Toolkit (SET)")
except:
    pass
