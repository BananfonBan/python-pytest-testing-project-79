import os
from pathlib import Path
import pytest
import pook
from PageLoader.page_loader import download


class fake_request:
    def __init__(self, data):
        self.text = data

    def get(self, url, headers):
        return self


@pytest.fixture
def data_html():
    path_dir = Path.cwd()
    with open(f"{path_dir}/tests/Example.html", 'r') as f:
        data = f.read()
        return data


@pook.on
def test_download_push_request(tmp_path):
    mock = pook.get('http://test.com')
    assert mock.calls == 0
    download('http://test.com', path_to_file=tmp_path)
    assert mock.calls == 1


def test_download_create_correct_file(tmp_path, data_html):
    download("https://test.io/1", path_to_file=tmp_path, client=fake_request(data_html))

    with open(f"{tmp_path}/test-io-1.html", "r") as result_file:
        file_data = result_file.read()

    path_file = Path(os.path.join(Path(tmp_path), "test-io-1.html"))
    assert path_file.exists()

    assert file_data == data_html
