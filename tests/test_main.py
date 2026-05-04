import pytest

from app.main import main


def test_main_prints_greeting(
    capsys: pytest.CaptureFixture[str], expected_greeting: str
) -> None:
    main()
    captured = capsys.readouterr()
    assert captured.out == expected_greeting
