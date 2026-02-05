"""Unit tests for ContractMonth value object.

Tests are organized by functionality:
- T013: Creation and validation
- T014: parse() with Japanese formats
- T015: Conversion methods (to_yyyymm, to_japanese)
- T016: Comparison and hashing
"""

import pytest
from pydantic import ValidationError

from marketsched import ContractMonth, ContractMonthParseError


class TestContractMonthCreation:
    """T013: Unit tests for ContractMonth creation and validation."""

    def test_create_with_valid_year_month(self) -> None:
        """ContractMonth can be created with valid year and month."""
        cm = ContractMonth(year=2026, month=3)
        assert cm.year == 2026
        assert cm.month == 3

    def test_create_with_month_1(self) -> None:
        """ContractMonth accepts month=1 (January)."""
        cm = ContractMonth(year=2026, month=1)
        assert cm.month == 1

    def test_create_with_month_12(self) -> None:
        """ContractMonth accepts month=12 (December)."""
        cm = ContractMonth(year=2026, month=12)
        assert cm.month == 12

    def test_reject_month_0(self) -> None:
        """ContractMonth rejects month=0."""
        with pytest.raises(ValueError, match="month"):
            ContractMonth(year=2026, month=0)

    def test_reject_month_13(self) -> None:
        """ContractMonth rejects month=13."""
        with pytest.raises(ValueError, match="month"):
            ContractMonth(year=2026, month=13)

    def test_reject_negative_month(self) -> None:
        """ContractMonth rejects negative month."""
        with pytest.raises(ValueError, match="month"):
            ContractMonth(year=2026, month=-1)

    def test_reject_negative_year(self) -> None:
        """ContractMonth rejects negative year."""
        with pytest.raises(ValueError, match="year"):
            ContractMonth(year=-1, month=3)

    def test_accept_far_future_year(self) -> None:
        """ContractMonth accepts far future year (e.g., 2099)."""
        cm = ContractMonth(year=2099, month=12)
        assert cm.year == 2099

    def test_immutable(self) -> None:
        """ContractMonth is immutable (frozen)."""
        cm = ContractMonth(year=2026, month=3)
        with pytest.raises((AttributeError, TypeError, ValidationError)):
            cm.year = 2027  # type: ignore[misc]


class TestContractMonthParse:
    """T014: Unit tests for ContractMonth.parse() with Japanese formats."""

    def test_parse_2digit_year_japanese(self) -> None:
        """Parse '26年3月限' -> year=2026, month=3."""
        cm = ContractMonth.parse("26年3月限")
        assert cm.year == 2026
        assert cm.month == 3

    def test_parse_4digit_year_japanese(self) -> None:
        """Parse '2026年3月限' -> year=2026, month=3."""
        cm = ContractMonth.parse("2026年3月限")
        assert cm.year == 2026
        assert cm.month == 3

    def test_parse_2digit_year_99_becomes_2099(self) -> None:
        """Parse '99年12月限' -> year=2099, month=12."""
        cm = ContractMonth.parse("99年12月限")
        assert cm.year == 2099
        assert cm.month == 12

    def test_parse_2digit_year_00_becomes_2000(self) -> None:
        """Parse '00年1月限' -> year=2000, month=1."""
        cm = ContractMonth.parse("00年1月限")
        assert cm.year == 2000
        assert cm.month == 1

    def test_parse_single_digit_month(self) -> None:
        """Parse '26年1月限' -> month=1."""
        cm = ContractMonth.parse("26年1月限")
        assert cm.month == 1

    def test_parse_double_digit_month(self) -> None:
        """Parse '26年12月限' -> month=12."""
        cm = ContractMonth.parse("26年12月限")
        assert cm.month == 12

    def test_parse_invalid_format_no_year(self) -> None:
        """Parse '3月限' raises ContractMonthParseError."""
        with pytest.raises(ContractMonthParseError):
            ContractMonth.parse("3月限")

    def test_parse_invalid_format_no_限(self) -> None:
        """Parse '26年3月' raises ContractMonthParseError."""
        with pytest.raises(ContractMonthParseError):
            ContractMonth.parse("26年3月")

    def test_parse_empty_string(self) -> None:
        """Parse '' raises ContractMonthParseError."""
        with pytest.raises(ContractMonthParseError):
            ContractMonth.parse("")

    def test_parse_invalid_month_13(self) -> None:
        """Parse '26年13月限' raises ContractMonthParseError."""
        with pytest.raises(ContractMonthParseError):
            ContractMonth.parse("26年13月限")

    def test_parse_with_whitespace(self) -> None:
        """Parse ' 26年3月限 ' (with whitespace) succeeds."""
        cm = ContractMonth.parse(" 26年3月限 ")
        assert cm.year == 2026
        assert cm.month == 3

    def test_parse_yyyymm_format(self) -> None:
        """Parse '202603' -> year=2026, month=3."""
        cm = ContractMonth.parse("202603")
        assert cm.year == 2026
        assert cm.month == 3

    def test_parse_yyyy_mm_format(self) -> None:
        """Parse '2026-03' -> year=2026, month=3."""
        cm = ContractMonth.parse("2026-03")
        assert cm.year == 2026
        assert cm.month == 3


class TestContractMonthConversion:
    """T015: Unit tests for ContractMonth conversion methods."""

    def test_to_yyyymm(self) -> None:
        """to_yyyymm() returns '202603' for year=2026, month=3."""
        cm = ContractMonth(year=2026, month=3)
        assert cm.to_yyyymm() == "202603"

    def test_to_yyyymm_with_single_digit_month(self) -> None:
        """to_yyyymm() zero-pads single digit month."""
        cm = ContractMonth(year=2026, month=1)
        assert cm.to_yyyymm() == "202601"

    def test_to_japanese(self) -> None:
        """to_japanese() returns '2026年3月限' for year=2026, month=3."""
        cm = ContractMonth(year=2026, month=3)
        assert cm.to_japanese() == "2026年3月限"

    def test_to_japanese_single_digit_month(self) -> None:
        """to_japanese() does not zero-pad month."""
        cm = ContractMonth(year=2026, month=1)
        assert cm.to_japanese() == "2026年1月限"

    def test_to_japanese_double_digit_month(self) -> None:
        """to_japanese() handles double-digit month."""
        cm = ContractMonth(year=2026, month=12)
        assert cm.to_japanese() == "2026年12月限"


class TestContractMonthComparison:
    """T016: Unit tests for ContractMonth comparison and hashing."""

    def test_equal(self) -> None:
        """Two ContractMonth with same year/month are equal."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2026, month=3)
        assert cm1 == cm2

    def test_not_equal_different_month(self) -> None:
        """ContractMonth with different months are not equal."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2026, month=4)
        assert cm1 != cm2

    def test_not_equal_different_year(self) -> None:
        """ContractMonth with different years are not equal."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2027, month=3)
        assert cm1 != cm2

    def test_less_than_by_year(self) -> None:
        """ContractMonth compares by year first."""
        cm1 = ContractMonth(year=2025, month=12)
        cm2 = ContractMonth(year=2026, month=1)
        assert cm1 < cm2

    def test_less_than_by_month(self) -> None:
        """ContractMonth compares by month when year is same."""
        cm1 = ContractMonth(year=2026, month=2)
        cm2 = ContractMonth(year=2026, month=3)
        assert cm1 < cm2

    def test_less_than_or_equal(self) -> None:
        """<= works correctly."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2026, month=3)
        cm3 = ContractMonth(year=2026, month=4)
        assert cm1 <= cm2
        assert cm1 <= cm3

    def test_greater_than(self) -> None:
        """> works correctly."""
        cm1 = ContractMonth(year=2026, month=4)
        cm2 = ContractMonth(year=2026, month=3)
        assert cm1 > cm2

    def test_greater_than_or_equal(self) -> None:
        """>= works correctly."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2026, month=3)
        cm3 = ContractMonth(year=2026, month=2)
        assert cm1 >= cm2
        assert cm1 >= cm3

    def test_hashable(self) -> None:
        """ContractMonth is hashable."""
        cm = ContractMonth(year=2026, month=3)
        assert hash(cm) is not None

    def test_same_hash_for_equal_objects(self) -> None:
        """Equal ContractMonth objects have same hash."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2026, month=3)
        assert hash(cm1) == hash(cm2)

    def test_usable_as_dict_key(self) -> None:
        """ContractMonth can be used as dict key."""
        cm = ContractMonth(year=2026, month=3)
        d = {cm: "value"}
        assert d[cm] == "value"
        # Access with equivalent object
        cm2 = ContractMonth(year=2026, month=3)
        assert d[cm2] == "value"

    def test_usable_in_set(self) -> None:
        """ContractMonth can be used in set."""
        cm1 = ContractMonth(year=2026, month=3)
        cm2 = ContractMonth(year=2026, month=3)  # Duplicate
        cm3 = ContractMonth(year=2026, month=4)
        s = {cm1, cm2, cm3}
        assert len(s) == 2  # cm1 and cm2 are same

    def test_sortable(self) -> None:
        """List of ContractMonth can be sorted."""
        cms = [
            ContractMonth(year=2027, month=1),
            ContractMonth(year=2026, month=3),
            ContractMonth(year=2026, month=1),
        ]
        sorted_cms = sorted(cms)
        assert sorted_cms[0] == ContractMonth(year=2026, month=1)
        assert sorted_cms[1] == ContractMonth(year=2026, month=3)
        assert sorted_cms[2] == ContractMonth(year=2027, month=1)


class TestContractMonthRepr:
    """Test string representation of ContractMonth."""

    def test_repr(self) -> None:
        """repr() returns readable representation."""
        cm = ContractMonth(year=2026, month=3)
        assert "2026" in repr(cm)
        assert "3" in repr(cm)

    def test_str(self) -> None:
        """str() returns Japanese format."""
        cm = ContractMonth(year=2026, month=3)
        assert str(cm) == "2026年3月限"
