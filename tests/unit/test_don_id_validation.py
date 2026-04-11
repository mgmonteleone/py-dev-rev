"""Unit tests for the DON ID validation utilities."""

import pytest

from devrev_mcp.utils.don_id import parse_don_type, validate_don_id


class TestParseDonType:
    """Tests for parse_don_type()."""

    @pytest.mark.parametrize(
        "don_id, expected",
        [
            ("don:core:dvrv-us-1:devo/1:account/123", "account"),
            ("don:core:dvrv-us-1:devo/1:revo/abc", "revo"),
            ("don:core:dvrv-us-1:devo/1:ticket/456", "ticket"),
            ("don:identity:dvrv-us-1:devo/1:devu/789", "devu"),
        ],
    )
    def test_parse_don_type_returns_correct_type_for_valid_ids(
        self, don_id: str, expected: str
    ) -> None:
        """Verify that valid DON IDs return the correct type segment."""
        assert parse_don_type(don_id) == expected

    def test_parse_don_type_empty_string_returns_none(self) -> None:
        """Empty string is not a DON ID — should return None."""
        assert parse_don_type("") is None

    def test_parse_don_type_display_id_returns_none(self) -> None:
        """Display IDs like ACC-12345 are not DON IDs — should return None."""
        assert parse_don_type("ACC-12345") is None

    def test_parse_don_type_random_string_returns_none(self) -> None:
        """Arbitrary strings that don't start with 'don:' return None."""
        assert parse_don_type("some-random-id") is None

    def test_parse_don_type_too_few_segments_returns_none(self) -> None:
        """A DON-prefixed string with fewer than 5 colon-segments returns None."""
        # Only 4 segments: don, core, dvrv-us-1, account/123
        assert parse_don_type("don:core:dvrv-us-1:account/123") is None

    def test_parse_don_type_last_segment_without_slash_returns_none(self) -> None:
        """Last segment must contain '/'; without it the type cannot be parsed."""
        assert parse_don_type("don:core:dvrv-us-1:devo/1:account") is None

    def test_parse_don_type_identity_domain_revo(self) -> None:
        """DON IDs using the identity domain should parse correctly."""
        don_id = "don:identity:dvrv-us-1:devo/11Ca9baGrM:revo/CHjPMe8K"
        assert parse_don_type(don_id) == "revo"


class TestValidateDonId:
    """Tests for validate_don_id()."""

    # ------------------------------------------------------------------ #
    # Happy-path tests                                                     #
    # ------------------------------------------------------------------ #

    def test_validate_don_id_correct_type_does_not_raise(self) -> None:
        """Matching type should pass without raising."""
        validate_don_id(
            "don:core:dvrv-us-1:devo/1:account/123",
            "account",
            "devrev_accounts_get",
        )

    def test_validate_don_id_non_don_id_passes_silently(self) -> None:
        """Non-DON IDs (e.g. display IDs) pass through without error."""
        validate_don_id("ACC-12345", "account", "devrev_accounts_get")

    def test_validate_don_id_empty_string_passes_silently(self) -> None:
        """Empty string does not start with 'don:' and passes silently."""
        validate_don_id("", "account", "devrev_accounts_get")

    def test_validate_don_id_list_one_matching_type_passes(self) -> None:
        """A ticket ID is valid when expected_types includes 'ticket'."""
        validate_don_id(
            "don:core:dvrv-us-1:devo/1:ticket/456",
            ["work", "ticket", "issue"],
            "devrev_works_get",
        )

    # ------------------------------------------------------------------ #
    # Error-raising tests                                                  #
    # ------------------------------------------------------------------ #

    def test_validate_don_id_wrong_type_raises_value_error(self) -> None:
        """A DON ID whose type doesn't match expected_types raises ValueError."""
        with pytest.raises(ValueError):
            validate_don_id(
                "don:identity:dvrv-us-1:devo/1:revo/CHj",
                "account",
                "devrev_accounts_get",
            )

    def test_validate_don_id_error_message_contains_tool_name(self) -> None:
        """The error message names the tool that rejected the ID."""
        with pytest.raises(ValueError, match="devrev_accounts_get"):
            validate_don_id(
                "don:identity:dvrv-us-1:devo/1:revo/CHj",
                "account",
                "devrev_accounts_get",
            )

    def test_validate_don_id_error_message_contains_actual_type_name(self) -> None:
        """The error message includes the friendly name of the actual type."""
        with pytest.raises(ValueError, match="rev_org"):
            validate_don_id(
                "don:identity:dvrv-us-1:devo/1:revo/CHj",
                "account",
                "devrev_accounts_get",
            )

    def test_validate_don_id_error_message_contains_expected_type_name(self) -> None:
        """The error message includes the friendly name of the expected type."""
        with pytest.raises(ValueError, match="account"):
            validate_don_id(
                "don:identity:dvrv-us-1:devo/1:revo/CHj",
                "account",
                "devrev_accounts_get",
            )

    def test_validate_don_id_error_message_suggests_correct_tool(self) -> None:
        """The error message suggests the tool that handles the supplied type."""
        with pytest.raises(ValueError, match="devrev_rev_orgs_get"):
            validate_don_id(
                "don:identity:dvrv-us-1:devo/1:revo/CHj",
                "account",
                "devrev_accounts_get",
            )

    def test_validate_don_id_list_no_matching_type_raises(self) -> None:
        """An account ID is rejected when none of the expected types match."""
        with pytest.raises(ValueError):
            validate_don_id(
                "don:core:dvrv-us-1:devo/1:account/123",
                ["work", "ticket", "issue"],
                "devrev_works_get",
            )

    def test_validate_don_id_unknown_parseable_type_raises_with_raw_type_name(
        self,
    ) -> None:
        """A DON ID whose type parses but isn't in DON_TYPE_MAP raises ValueError
        with the raw type name in the message."""
        with pytest.raises(ValueError, match="unknowntype"):
            validate_don_id(
                "don:core:dvrv-us-1:devo/1:unknowntype/999",
                "account",
                "devrev_accounts_get",
            )

    def test_validate_don_id_unparseable_don_id_raises_unrecognised_message(
        self,
    ) -> None:
        """A 'don:'-prefixed string whose last segment lacks '/' cannot be parsed;
        the error message describes it as 'unrecognised DON ID'."""
        with pytest.raises(ValueError, match="unrecognised DON ID"):
            validate_don_id(
                # 5 colon-segments but the last one has no '/', so parse_don_type → None
                "don:core:dvrv-us-1:devo/1:noslash",
                "account",
                "devrev_accounts_get",
            )
