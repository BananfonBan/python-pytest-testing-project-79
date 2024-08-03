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
    mock_1 = pook.get('http://test.com')
    assert mock_1.calls == 0

    download(url="http://test.com", path_to_file=tmp_path)
    assert mock_1.calls == 1

    mock_2 = pook.get("http://test_2.io/download/push")
    download(url="http://test_2.io/download/push", path_to_file=tmp_path)
    assert mock_2.calls == 1

    mock_3 = pook.get("http://test.com/push/test")
    download(url="http://test.com/push/test", path_to_file=tmp_path)
    assert mock_3.calls == 1


def test_download_create_correct_file(tmp_path, data_html):
    name_file = download(tmp_path, "https://test.io/1", client=fake_request(data_html))

    with open(f"{tmp_path}/test-io-1.html", "r") as result_file:
        file_data = result_file.read()

    path_file = Path(os.path.join(Path(tmp_path), "test-io-1.html"))
    assert path_file.exists()
    assert os.path.normpath(name_file) == os.path.normpath(path_file)
    assert file_data == data_html
