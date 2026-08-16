import unittest
from unittest import mock
from client import Client


class TestClient(unittest.TestCase):
    def test_signature_changes_with_ts(self):
        c = Client("https://x.test", "k")
        s1 = c._sign("GET", "/a", b"", "1")
        s2 = c._sign("GET", "/a", b"", "2")
        self.assertNotEqual(s1, s2)

    def test_retry_on_500(self):
        c = Client("https://x.test", "k", config={"timeout": 1})
        with mock.patch("urllib.request.urlopen", side_effect=[
            urllib.error.HTTPError("url", 500, "err", {}, None),
            mock.Mock(read=lambda: b"{}"),
        ]):
            self.assertEqual(c.get("/v1/data"), b"{}")


if __name__ == "__main__":
    unittest.main()