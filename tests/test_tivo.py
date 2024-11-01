import pytest

from tivo.cli import main


def test_list() -> None:
    main(["list"])


def test_getch_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["getch", "--help"])
    assert err.value.code == 0


def test_setch_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["setch", "--help"])
    assert err.value.code == 0


def test_upch_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["upch", "--help"])
    assert err.value.code == 0


def test_downch_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["downch", "--help"])
    assert err.value.code == 0
