import pytest

from tivo.cli import main


def test_version() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--version"])
    assert err.value.code == 0


def test_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--help"])
    assert err.value.code == 0


def test_md_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--md-help"])
    assert err.value.code == 0


def test_long_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--long-help"])
    assert err.value.code == 0


def test_bogus_option() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--bogus-option"])
    assert err.value.code == 2


def test_bogus_argument() -> None:
    with pytest.raises(SystemExit) as err:
        main(["bogus-argument"])
    assert err.value.code == 2


def test_print_config() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--print-config"])
    assert err.value.code == 0


def test_print_url() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--print-url"])
    assert err.value.code == 0


def test_debug() -> None:
    with pytest.raises(SystemExit) as err:
        main(["-X"])
    assert err.value.code == 0


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
