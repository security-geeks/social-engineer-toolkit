import ast
import os
from pathlib import Path

import pytest

import src.core.setcore as setcore
import src.qrcode.qrgenerator as qrgenerator


def test_safe_join_webroot_allows_files_under_root(tmp_path):
    webroot = tmp_path / "web_clone"
    webroot.mkdir()

    resolved = setcore.safe_join_webroot(str(webroot), "/assets/site.css")

    assert resolved == str(webroot / "assets/site.css")


def test_safe_join_webroot_blocks_traversal(tmp_path):
    webroot = tmp_path / "web_clone"
    webroot.mkdir()

    assert setcore.safe_join_webroot(str(webroot), "/../secret.txt") is None
    assert setcore.safe_join_webroot(str(webroot), "/%2e%2e/secret.txt") is None


def test_meta_path_accepts_configured_msfconsole_executable(monkeypatch):
    def fake_check_config(key):
        if key == "METASPLOIT_PATH=":
            return "/opt/metasploit-framework/bin/msfconsole"
        if key == "METASPLOIT_MODE=":
            return "ON"
        return ""

    monkeypatch.setattr(setcore, "check_config", fake_check_config)
    monkeypatch.setattr(
        setcore.os.path,
        "isfile",
        lambda path: path == "/opt/metasploit-framework/bin/msfconsole",
    )

    assert setcore.meta_path() == "/opt/metasploit-framework/bin/"


def test_smtp_auth_b64_returns_ascii_text():
    encoded = setcore.smtp_auth_b64("user@example.com")

    assert encoded == "dXNlckBleGFtcGxlLmNvbQ=="
    assert isinstance(encoded, str)


def test_legacy_payload_binary_path_reports_missing_payload(tmp_path):
    with pytest.raises(FileNotFoundError) as excinfo:
        setcore.legacy_payload_binary_path(str(tmp_path), "shellcode/pyinject")

    assert "pyinjector.binary" in str(excinfo.value)
    assert "legacy Java shellcode injector payload is unavailable" in str(excinfo.value)


def test_harvester_writes_binary_static_files_without_encoding():
    source = Path("src/webattack/harvester/harvester.py").read_text()

    assert 'open(requested_file, "rb")' in source
    assert "line = line.encode('utf-8')" not in source


def test_legacy_payload_injectors_use_valid_choice_names():
    source = Path("src/core/payloadgen/create_payloads.py").read_text()

    assert "legacy_payload_binary_path(definepath, choice1)" in source
    assert "shellcode/multipyiject" not in source


def test_binary2teensy_no_longer_uses_removed_python2_builtins():
    tree = ast.parse(Path("src/teensy/binary2teensy.py").read_text())

    removed_builtin_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"file", "unicode"}
    }

    assert removed_builtin_calls == set()


def test_qrcode_generator_creates_reports_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(qrgenerator.core, "userconfigpath", str(tmp_path) + os.sep)

    qrgenerator.gen_qrcode("https://example.com")

    assert (tmp_path / "reports/qrcode_attack.png").is_file()


def test_set_http_server_uses_python3_header_and_aes_byte_handling():
    source = Path("src/payloads/set_payloads/set_http_server.py").read_text()

    assert ".headers.get(" in source
    assert ".headers.getheader(" not in source
    assert 'secret = b"' in source
    assert "AES.new(secret, AES.MODE_ECB)" in source
    assert "[0-9a-fA-F]" in source


def test_encrypt_aes_accepts_bytes_secret_and_text_payload():
    encrypted = setcore.encryptAES(b"1" * 32, "payload")

    assert isinstance(encrypted, str)
    assert encrypted
    assert not encrypted.startswith("b'")


def test_payload_aes_modules_use_explicit_mode_and_python3_urllib():
    paths = [
        Path("src/core/setcore.py"),
        Path("src/payloads/set_payloads/http_shell.py"),
        Path("src/payloads/set_payloads/listener.py"),
    ]

    for path in paths:
        source = path.read_text()
        assert "AES.new(secret, AES.MODE_ECB)" in source
        assert "AES.new(secret)" not in source

    http_shell = Path("src/payloads/set_payloads/http_shell.py").read_text()
    assert "from urllib import parse, request" in http_shell
    assert "urllib.request" not in http_shell
    assert "urllib.parse" not in http_shell

    listener = Path("src/payloads/set_payloads/listener.py").read_text()
    assert "import _thread as thread" in listener
    assert "conn.sendall(_socket_bytes(" in listener
    assert "conn.send(str(" not in listener


def test_remaining_python3_text_boundaries_are_normalized():
    sd2teensy = Path("src/teensy/sd2teensy.py").read_text()
    assert 'base64.b64encode(powershell_command.encode("utf-8")).decode("ascii")' in sd2teensy
    assert "core.powershell_encodedcommand(powershell_command)" in sd2teensy

    smtp_web = Path("src/phishing/smtp/client/smtp_web.py").read_text()
    assert 'str(base64.b64encode(to.encode()))' not in smtp_web
    assert "smtp_auth_b64(to)" in smtp_web

    setcore = Path("src/core/setcore.py").read_text()
    assert "# import the threading, socketserver, and simplehttpserver\n        import thread" not in setcore
    assert 'conn.sendall(command.encode("utf-8"))' in setcore
    assert "conn.send(command)" not in setcore


def test_smtp_client_threads_sendmail_callable_instead_of_result():
    source = Path("src/phishing/smtp/client/smtp_client.py").read_text()

    assert "thread.start_new_thread(mailServer.sendmail(\n" not in source
    assert "thread.start_new_thread(mailServer.sendmail,\n" in source


def test_teensy_file_operations_avoid_shell_wrappers():
    binary2teensy = Path("src/teensy/binary2teensy.py").read_text()
    sd2teensy = Path("src/teensy/sd2teensy.py").read_text()
    teensy = Path("src/teensy/teensy.py").read_text()

    assert 'subprocess.Popen("rm ' not in binary2teensy
    assert 'subprocess.Popen("msfconsole -r ' not in binary2teensy
    assert 'subprocess.Popen("rm ' not in sd2teensy
    assert 'subprocess.Popen("cp ' not in teensy
    assert "os.remove(random_filename)" in binary2teensy
    assert "os.remove(answer_path)" in binary2teensy
    assert "subprocess.Popen([\"msfconsole\", \"-r\", answer_path])" in binary2teensy
    assert "os.remove(random_filename)" in sd2teensy
    assert "shutil.copyfile(metasploit_exec_path, os.path.join(webclone_path, \"x.exe\"))" in teensy


def test_applet_and_ratte_file_operations_avoid_shell_copy_wrappers():
    smtp_client = Path("src/phishing/smtp/client/smtp_client.py").read_text()
    setcore = Path("src/core/setcore.py").read_text()
    ratte = Path("modules/ratte_module.py").read_text()
    ratte_only = Path("modules/ratte_only_module.py").read_text()

    assert 'subprocess.Popen("cp ' not in smtp_client
    assert 'subprocess.Popen("cp %s/msf.exe' not in setcore
    assert 'subprocess.Popen(\n        "cp %s/Signed_Update.jar' not in setcore
    assert 'subprocess.Popen("cp src/payloads/ratte/ratte.binary' not in ratte
    assert 'subprocess.Popen("cp %s/Signed_Update.jar' not in ratte
    assert 'subprocess.Popen("cp %s/ratteM.exe' not in ratte
    assert "if filename not in (0, \"\"):" in setcore
    assert "if applet_name in (0, \"\"):" in setcore
    assert "shutil.copyfile(file_format, os.path.join(userconfigpath, filename1))" in smtp_client
    assert 'os.path.join(userconfigpath, "rand_gen")' in ratte
    assert 'os.path.join(userconfigpath, "ratteM.exe")' in ratte
    assert "patched = data" in ratte
    assert "patched = data" in ratte_only
    assert 'to_replace = (core.grab_ipaddress() + ":80").encode("utf-8")' in ratte


def test_binary_payload_patchers_use_bytes_markers():
    payloadprep = Path("src/core/payloadprep.py").read_text()
    dll_hijacking = Path("src/webattack/dll_hijacking/hijacking.py").read_text()

    assert "data.replace(str(" not in payloadprep
    assert "data.replace(str(" not in dll_hijacking
    assert "def _binary_marker(value, marker):" in payloadprep
    assert "def _nul_terminated(value):" in payloadprep
    assert "data.replace(_binary_marker(exe_name, \"X\"), _nul_terminated(exe_name), 1)" in payloadprep
    assert "data.replace(_binary_marker(webserver, \"S\"), _nul_terminated(webserver), 1)" in payloadprep
    assert "data.replace(_binary_marker(ipaddr, \"M\"), _nul_terminated(ipaddr), 1)" in payloadprep
    assert "data.replace(_binary_marker(port, \"Y\"), _nul_terminated(port), 1)" in payloadprep
    assert 'host = ((len(ipaddr) + 1) * "X").encode("ascii")' in dll_hijacking
    assert 'filewrite.write(data.replace(host, (ipaddr + "\\x00").encode("utf-8"), 1))' in dll_hijacking
    assert 'subprocess.Popen("mkdir " + userconfigpath + "dll"' not in dll_hijacking
    assert 'subprocess.Popen("cp %s/msf.exe %s/src/html/"' not in dll_hijacking
    assert 'subprocess.Popen("cd %s/dll;rar a %s/template.rar *' not in dll_hijacking
    assert 'subprocess.Popen("rar", shell=True' not in dll_hijacking


def test_java_payload_encoding_uses_generated_data_not_literals():
    source = Path("src/core/payloadgen/create_payloads.py").read_text()

    assert "base64.b64encode(b'data')" not in source
    assert "base64.b64encode(b'secret')" not in source
    assert 'for _ in range(11):' in source
    assert 'data = base64.b64encode(data.encode("utf-8")).decode("ascii")' in source
    assert 'secret = base64.b64encode(secret).decode("ascii")' in source
    assert 'base_encode = base64.b64encode(x86).decode("ascii")' in source
    assert 'subprocess.Popen("cp %s/shellcodeexec.custom' not in source
    assert 'subprocess.Popen("mv %s/web_clone/index.html.new' not in source
    assert 'os.path.join(userconfigpath, "web_clone", "index.html.new")' in source


def test_harvester_uses_python_file_operations_for_pem_files():
    source = Path("src/webattack/harvester/harvester.py").read_text()

    assert 'subprocess.Popen("cp %s/CA/*.pem' not in source
    assert 'subprocess.Popen("rm -rf %s/CA;cp *.pem' not in source
    assert 'subprocess.Popen("cp %s %s/newcert.pem' not in source
    assert 'subprocess.Popen("cp %s %s/newreq.pem' not in source
    assert 'subprocess.Popen("cp %s/*.pem %s/web_clone/"' not in source
    assert "def copy_pem_files(source_pattern, destination):" in source
    assert 'shutil.rmtree(os.path.join(userconfigpath, "CA"), ignore_errors=True)' in source
    assert 'rex = re.compile(\'%([0-9a-fA-F][0-9a-fA-F])\', re.M)' in source


def test_core_export_and_upx_file_operations_avoid_shell_wrappers():
    source = Path("src/core/setcore.py").read_text()

    assert 'subprocess.Popen("mkdir \'%s\';cp %s/web_clone/*' not in source
    assert 'subprocess.Popen("mv %s/temp.binary %s"' not in source
    assert '"%s -9 -q -o %s/temp.binary %s"' not in source
    assert 'shutil.copytree(source_path, destination_path, dirs_exist_ok=True)' in source
    assert 'shutil.copy2(source_path, destination_path)' in source
    assert 'subprocess.Popen(\n            [upx_path, "-9", "-q", "-o", temp_binary_path, path_to_file]' in source
    assert 'data.replace(b"UPX", random_string.encode("ascii"), 4)' in source
    assert "os.replace(temp_binary_path, path_to_file)" in source


def test_java_signing_helpers_avoid_shell_file_operations():
    paths = [
        Path("src/webattack/java_applet/unsigned.py"),
        Path("src/webattack/java_applet/sign_jar.py"),
        Path("src/html/unsigned/self_sign.py"),
        Path("src/html/unsigned/verified_sign.py"),
    ]

    combined = "\n".join(path.read_text() for path in paths)

    assert 'subprocess.Popen("rm ' not in combined
    assert 'subprocess.Popen("cp ' not in combined
    assert 'subprocess.Popen("mv ' not in combined
    assert "shell=True" not in combined
    assert 'subprocess.Popen(["javac", "Java.java"])' in combined
    assert 'subprocess.Popen(["jar", "cvf", "Java_Update.jar", "Java.class"])' in combined
    assert 'shutil.move("Signed_Update.jar", os.path.join(core.userconfigpath, "Signed_Update.jar"))' in combined
    assert 'shutil.move("Signed_Update.jar", os.path.join(core.userconfigpath, "Signed_Update.jar.orig"))' in combined


def test_webattack_setup_helpers_avoid_shell_file_operations():
    report_generator = Path("src/webattack/harvester/report_generator.py").read_text()
    tabnabbing = Path("src/webattack/tabnabbing/tabnabbing.py").read_text()
    multiattack = Path("src/webattack/multi_attack/multiattack.py").read_text()
    setssl = Path("src/core/ssl/setssl.py").read_text()

    assert 'subprocess.Popen("cp -rf %s/src/core/reports/files' not in report_generator
    assert 'subprocess.Popen("mv %s/web_clone/index.html %s/web_clone/index2.html"' not in tabnabbing
    assert 'subprocess.Popen("rm -rf %s/web_clone;mkdir %s/web_clone/"' not in multiattack
    assert 'subprocess.Popen("mkdir CA;cd CA;mkdir newcerts private"' not in setssl
    assert "subprocess.Popen(\"echo '01' > serial;touch index.txt\"" not in setssl
    assert 'subprocess.Popen(\n    "cp private/cakey.pem newreq.pem;cp *.pem ../"' not in setssl
    assert 'dirs_exist_ok=True' in report_generator
    assert 'from urllib import request' in tabnabbing
    assert 'shutil.rmtree(web_clone_path)' in multiattack
    assert 'os.makedirs(os.path.join("CA", "newcerts"), exist_ok=True)' in setssl
    assert '"openssl", "req",' in setssl
    assert '"-extensions", "v3_ca"' in setssl


def test_spawn_uses_python_file_operations_for_staging():
    source = Path("src/html/spawn.py").read_text()

    assert 'subprocess.Popen("mv %s/web_clone/index.html.new %s/web_clone/index.html"' not in source
    assert 'subprocess.Popen("cp %s/src/html/*.bin %s' not in source
    assert 'subprocess.Popen("rm %s/index.html' not in source
    assert "def copy_matches(pattern, destination):" in source
    assert "def remove_matches(pattern):" in source
    assert 'if applet_name in (0, ""):' in source
    assert 'copy_matches(os.path.join(definepath, "src", "html", "*.bin"), apache_path)' in source
    assert 'copy_matches(os.path.join(userconfigpath, "web_clone", "*"), apache_path)' in source
    assert 'remove_matches(os.path.join(apache_path, "Signed*"))' in source


def test_payload_copy_helpers_avoid_shell_file_operations():
    autorun = Path("src/autorun/autolaunch.py").read_text()
    mssql = Path("src/fasttrack/mssql.py").read_text()
    create_payload = Path("src/core/msf_attacks/create_payload.py").read_text()

    assert 'subprocess.Popen("rm -rf {0} 1> /dev/null 2> /dev/null;"' not in autorun
    assert 'subprocess.Popen("cp %s/msf.exe %s/1msf.exe"' not in mssql
    assert 'subprocess.Popen("cp " + msfpath + "local/%s %s"' not in create_payload
    assert 'subprocess.Popen("mkdir %s/web_clone;cp src/html/msf.exe %s/web_clone/x"' not in create_payload
    assert 'subprocess.Popen("cp src/html/msf.exe %s/x.exe"' not in create_payload
    assert "def reset_autorun_path():" in autorun
    assert 'glob.glob(os.path.join(core.userconfigpath, "dll", "*"))' in autorun
    assert "import _thread as thread" in mssql
    assert 'payload_filename = os.path.join(web_path, "1msf.exe")' in mssql
    assert 'shutil.copyfile("src/html/msf.exe", os.path.join(web_clone_path, "x"))' in create_payload
