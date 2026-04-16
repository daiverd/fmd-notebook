from datetime import date

import pytest
from tests.conftest import get_csrf_token


class TestCanonicalization:
    def test_view_md_redirects_to_stem(self, client):
        r = client.get("/view/foo.md")
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/view/foo")

    def test_edit_md_redirects_to_stem(self, client):
        r = client.get("/edit/foo.md")
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/edit/foo")


class TestMissingFile:
    def test_view_missing_redirects_to_edit(self, client):
        r = client.get("/view/nonexistent")
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/edit/nonexistent")

    def test_edit_missing_shows_new_file(self, client):
        r = client.get("/edit/nonexistent")
        assert r.status_code == 200
        assert "# new file" in r.get_data(as_text=True)


class TestTraversal:
    @pytest.mark.parametrize("path", [
        "/view/../../etc/passwd",
        "/edit/../../etc/passwd",
    ])
    def test_get_traversal_404(self, client, path):
        r = client.get(path)
        assert r.status_code == 404

    def test_post_traversal_no_file_escape(self, client, isolated):
        token = get_csrf_token(client, "/edit/legit")
        r = client.post("/edit/../../etc/passwd",
                        data={"text": "pwned", "csrf_token": token})
        assert r.status_code == 404
        assert not (isolated.base_dir.parent / "passwd").exists()


class TestCSRF:
    def test_post_without_token_400(self, client):
        r = client.post("/edit/foo", data={"text": "x"})
        assert r.status_code == 400

    def test_post_wrong_token_400(self, client):
        r = client.post("/edit/foo", data={"text": "x", "csrf_token": "garbage"})
        assert r.status_code == 400

    def test_post_valid_token_saves(self, client):
        token = get_csrf_token(client, "/edit/foo")
        r = client.post("/edit/foo", data={"text": "ok\n", "csrf_token": token})
        assert r.status_code == 302


class TestSaveRoundTrip:
    def test_newlines_preserved(self, client, isolated):
        token = get_csrf_token(client, "/edit/nlchk")
        client.post("/edit/nlchk", data={"text": "a\r\nb\r\nc\r\n", "csrf_token": token})
        assert (isolated.base_dir / "nlchk.md").read_bytes() == b"a\nb\nc\n"

    def test_dulwich_commit_created(self, client, isolated):
        token = get_csrf_token(client, "/edit/commitchk")
        client.post("/edit/commitchk", data={"text": "x\n", "csrf_token": token})
        head = isolated.repo[isolated.repo.head()]
        assert b"commitchk" in head.message

    def test_redirect_to_view_stem(self, client):
        token = get_csrf_token(client, "/edit/redir")
        r = client.post("/edit/redir", data={"text": "x", "csrf_token": token})
        assert r.headers["Location"].endswith("/view/redir")

    def test_view_after_save_200(self, client):
        token = get_csrf_token(client, "/edit/roundtrip")
        client.post("/edit/roundtrip", data={"text": "hello\n", "csrf_token": token})
        r = client.get("/view/roundtrip")
        assert r.status_code == 200
        assert "hello" in r.get_data(as_text=True)


class TestSubpaths:
    def test_parent_dirs_created(self, client, isolated):
        token = get_csrf_token(client, "/edit/a/b/c")
        client.post("/edit/a/b/c", data={"text": "hi\n", "csrf_token": token})
        assert (isolated.base_dir / "a" / "b" / "c.md").exists()

    def test_redirect_preserves_subpath(self, client):
        token = get_csrf_token(client, "/edit/a/b")
        r = client.post("/edit/a/b", data={"text": "x", "csrf_token": token})
        assert r.headers["Location"].endswith("/view/a/b")


class TestShortcuts:
    @pytest.mark.parametrize("name", [
        "yesterday", "today", "tomorrow",
        "last_week", "this_week", "next_week",
    ])
    def test_shortcut_redirects(self, client, name):
        r = client.get(f"/view/{name}")
        assert r.status_code == 302
        assert f"/view/{name}" != r.headers["Location"].split("http://localhost")[-1]

    def test_today_md_variant(self, client):
        r = client.get("/view/today.md")
        assert r.status_code == 302
        assert r.headers["Location"].endswith(f"/view/{date.today().isoformat()}")

    def test_project_scoped_shortcut(self, client):
        r = client.get("/view/proj/today")
        assert r.status_code == 302
        assert f"/view/proj/{date.today().isoformat()}" in r.headers["Location"]

    def test_shortcut_traversal_rejected(self, client):
        r = client.get("/view/../evil/today")
        assert r.status_code == 404

    def test_unknown_name_falls_through(self, client):
        r = client.get("/view/not_a_shortcut")
        assert r.status_code == 302
        assert r.headers["Location"].endswith("/edit/not_a_shortcut")


class TestTextareaEscape:
    def test_breakout_payload_escaped(self, client, isolated):
        (isolated.base_dir / "xss.md").write_text("</textarea><script>alert(1)</script>")
        html = client.get("/edit/xss").get_data(as_text=True)
        assert "</textarea><script>" not in html
        assert "&lt;/textarea&gt;" in html


class TestIndex:
    def test_lists_files_recursively(self, client, isolated):
        (isolated.base_dir / "a.md").write_text("a")
        (isolated.base_dir / "sub").mkdir()
        (isolated.base_dir / "sub" / "b.md").write_text("b")
        html = client.get("/").get_data(as_text=True)
        assert 'href="/view/a"' in html
        assert 'href="/view/sub/b"' in html

    def test_links_have_no_md_suffix(self, client, isolated):
        (isolated.base_dir / "foo.md").write_text("x")
        html = client.get("/").get_data(as_text=True)
        assert "/view/foo.md" not in html
        assert "/view/foo" in html
