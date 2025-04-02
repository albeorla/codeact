"""Tests for the LLM provider and parser implementations."""

from codeact.implementations.llm import RegexLLMOutputParser


def test_regex_llm_output_parser_thought():
    """Test that the parser correctly extracts thought content."""
    parser = RegexLLMOutputParser()
    output = "<thought>This is a test thought</thought>"
    result = parser.parse(output)
    assert result["thought"] == "This is a test thought"
    assert result["code_action"] is None
    assert result["solution"] is None
    assert result["raw_response"] == output


def test_regex_llm_output_parser_code_action():
    """Test that the parser correctly extracts code action content."""
    parser = RegexLLMOutputParser()
    output = "<execute>print('Hello, World!')</execute>"
    result = parser.parse(output)
    assert result["thought"] is None
    assert result["code_action"] == "print('Hello, World!')"
    assert result["solution"] is None
    assert result["raw_response"] == output


def test_regex_llm_output_parser_solution():
    """Test that the parser correctly extracts solution content."""
    parser = RegexLLMOutputParser()
    output = "<solution>This is the answer</solution>"
    result = parser.parse(output)
    assert result["thought"] is None
    assert result["code_action"] is None
    assert result["solution"] == "This is the answer"
    assert result["raw_response"] == output


def test_regex_llm_output_parser_combined():
    """Test that the parser correctly extracts combined content."""
    parser = RegexLLMOutputParser()
    output = """<thought>Let me think about this</thought>
<execute>print('Testing')</execute>
<solution>The answer is 42</solution>"""
    result = parser.parse(output)
    assert result["thought"] == "Let me think about this"
    assert result["code_action"] == "print('Testing')"
    assert result["solution"] == "The answer is 42"
    assert result["raw_response"] == output


def test_regex_llm_output_parser_fallback():
    """Test that the parser falls back to treating the whole output as a solution."""
    parser = RegexLLMOutputParser()
    output = "This is just plain text with no tags"
    result = parser.parse(output)
    assert result["thought"] is None
    assert result["code_action"] is None
    assert result["solution"] == output
    assert result["raw_response"] == output
