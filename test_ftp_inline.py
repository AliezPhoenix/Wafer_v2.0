"""Lightweight checks for inline FTP + heartbeat helpers (no PLC/FTP hardware)."""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestDownloadFilePath(unittest.TestCase):
    def test_local_path_not_appended_across_retries(self):
        from Functions import download_file

        calls = {"retry": 0}
        ftp = MagicMock()

        def voidcmd(_cmd):
            return

        def cwd(path):
            if calls["retry"] == 0:
                calls["retry"] += 1
                raise OSError("first fail")

        written = []

        def retrbinary(_cmd, callback, _bufsize):
            callback(b"a,b\n")

        ftp.voidcmd.side_effect = voidcmd
        ftp.cwd.side_effect = cwd
        ftp.retrbinary.side_effect = retrbinary

        with tempfile.TemporaryDirectory() as tmp:
            with patch("Functions.conn_ftp", return_value=(1, ftp)):
                ret = download_file(ftp, "/FTP", tmp, "CutLineMap.CSV", max_retries=2)
            self.assertEqual(ret, "OK")
            path = os.path.join(tmp, "CutLineMap.CSV")
            self.assertTrue(os.path.isfile(path))
            # Must be exactly one path join, not tmp/CutLineMap.CSV/CutLineMap.CSV
            self.assertFalse(os.path.isdir(os.path.join(tmp, "CutLineMap.CSV")))


class TestCommunicateReconnectLogic(unittest.TestCase):
    def test_connect_success_means_zero(self):
        # Document contract used by fixed retry: 0 success, 1 failure
        from Communicate import Communicate

        com = Communicate.__new__(Communicate)
        com.ip = "127.0.0.1"
        com.port = 9
        com.Sender = MagicMock()
        com.Sender.connect.side_effect = OSError("fail")
        com.Sender.close = MagicMock()
        self.assertEqual(Communicate.connect(com), 1)

        com.Sender.connect.side_effect = None
        self.assertEqual(Communicate.connect(com), 0)


if __name__ == "__main__":
    unittest.main()
