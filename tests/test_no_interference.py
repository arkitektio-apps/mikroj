from mikroj.main import MikroJ
import pytest


@pytest.mark.qt
def test_fetch_from_windowed_grant(qtbot):
    widget = MikroJ(auto_init=False)
    qtbot.addWidget(widget)
