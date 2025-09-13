import pytest

from delfino_core.vcs_tools import _sanitize_branch_name


class TestSanitizeBranchName:
    @staticmethod
    def test_should_keep_slash_character():
        assert _sanitize_branch_name("feature/branch") == "feature/branch"

    @staticmethod
    @pytest.mark.parametrize(
        "input_branch, expected_output",
        [
            # Single special character cases
            pytest.param("feature[branch", "feature_branch", id="single open bracket"),
            pytest.param("feature]branch", "feature_branch", id="single close bracket"),
            pytest.param("feature{branch", "feature_branch", id="single open brace"),
            pytest.param("feature}branch", "feature_branch", id="single close brace"),
            pytest.param("feature:branch", "feature_branch", id="single colon"),
            pytest.param("feature;branch", "feature_branch", id="single semicolon"),
            pytest.param("feature'branch", "feature_branch", id="single single quote"),
            pytest.param('feature"branch', "feature_branch", id="single double quote"),
            pytest.param("feature,branch", "feature_branch", id="single comma"),
            pytest.param("feature.branch", "feature_branch", id="single period"),
            pytest.param("feature<branch", "feature_branch", id="single less than"),
            pytest.param("feature>branch", "feature_branch", id="single greater than"),
            pytest.param("feature?branch", "feature_branch", id="single question mark"),
            pytest.param("feature+branch", "feature_branch", id="single plus"),
            pytest.param("feature=branch", "feature_branch", id="single equals"),
            pytest.param("feature(branch", "feature_branch", id="single open parenthesis"),
            pytest.param("feature)branch", "feature_branch", id="single close parenthesis"),
            pytest.param("feature*branch", "feature_branch", id="single asterisk"),
            pytest.param("feature#branch", "feature_branch", id="single hash"),
            pytest.param("feature!branch", "feature_branch", id="single exclamation mark"),
            pytest.param("feature~branch", "feature_branch", id="single tilde"),
            pytest.param("feature`branch", "feature_branch", id="single backtick"),
        ],
    )
    def test_should_replace_single_special_character_with_underscore(input_branch, expected_output):
        assert _sanitize_branch_name(input_branch) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        "input_branch, expected_output",
        [
            pytest.param("feature[{}]branch", "feature_branch", id="multiple brackets braces"),
            pytest.param("feature:;branch", "feature_branch", id="multiple colon semicolon"),
            pytest.param("feature'\"branch", "feature_branch", id="multiple quotes"),
            pytest.param("feature,.branch", "feature_branch", id="multiple comma period"),
            pytest.param("feature<>branch", "feature_branch", id="multiple less greater than"),
            pytest.param("feature?+=branch", "feature_branch", id="multiple question plus equals"),
            pytest.param("feature()*branch", "feature_branch", id="multiple parentheses asterisk"),
            pytest.param("feature#!branch", "feature_branch", id="multiple hash exclamation"),
            pytest.param("feature~`branch", "feature_branch", id="multiple tilde backtick"),
        ],
    )
    def test_should_replace_multiple_special_characters_with_underscore(input_branch, expected_output):
        assert _sanitize_branch_name(input_branch) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        "input_branch, expected_output",
        [
            pytest.param(
                "!ticket-123/feature description", "ticket-123/feature_description", id="with single character"
            ),
            pytest.param('("name"): feature branch', "name_feature_branch", id="with multiple characters"),
        ],
    )
    def test_should_strip_special_characters_from_the_start(input_branch, expected_output):
        assert _sanitize_branch_name(input_branch) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        "input_branch, expected_output",
        [
            pytest.param("feature branch.", "feature_branch", id="with single character"),
            pytest.param("(feature branch).", "feature_branch", id="with multiple characters"),
        ],
    )
    def test_should_strip_special_characters_from_the_end(input_branch, expected_output):
        assert _sanitize_branch_name(input_branch) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        "input_branch, expected_output",
        [
            pytest.param(
                "[ticket-123]/feature branch", "ticket-123/feature_branch", id="from the left with single character"
            ),
            pytest.param(
                "[ticket-123] /feature branch", "ticket-123/feature_branch", id="from the left with multiple characters"
            ),
            pytest.param(
                "ticket-123/ feature branch", "ticket-123/feature_branch", id="from the right with single character"
            ),
            pytest.param(
                "ticket-123/ 'feature branch'",
                "ticket-123/feature_branch",
                id="from the right with multiple characters",
            ),
        ],
    )
    def test_should_strip_special_characters_around_slash(input_branch, expected_output):
        assert _sanitize_branch_name(input_branch) == expected_output
