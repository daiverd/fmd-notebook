import re

import pytest
from dulwich.repo import Repo


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """Swap fmd.base_dir and fmd.repo to a per-test temp directory."""
    import fmd

    monkeypatch.setattr(fmd, "base_dir", tmp_path)
    monkeypatch.setattr(fmd, "repo", Repo.init(str(tmp_path)))
    return fmd


@pytest.fixture
def client(isolated):
    """Flask test client wired to the isolated temp notebook."""
    return isolated.app.test_client()


def get_csrf_token(client, path="/edit/_token"):
    """Fetch a CSRF token from an edit page GET."""
    html = client.get(path).get_data(as_text=True)
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, f"no CSRF token found in {path}"
    return m.group(1)
