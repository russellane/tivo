import pytest

from tivo.cli import main


def test_list():
    main(["list"])


def test_getch_help():
    with pytest.raises(SystemExit) as err:
        main(["getch", "--help"])
    assert err.value.code == 0


def test_setch_help():
    with pytest.raises(SystemExit) as err:
        main(["setch", "--help"])
    assert err.value.code == 0


def test_upch_help():
    with pytest.raises(SystemExit) as err:
        main(["upch", "--help"])
    assert err.value.code == 0


def test_downch_help():
    with pytest.raises(SystemExit) as err:
        main(["downch", "--help"])
    assert err.value.code == 0
