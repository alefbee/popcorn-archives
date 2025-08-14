from popcorn_archives.core import parse_movie_title

def test_parse_with_parentheses():
    """Tests the 'Title (YYYY)' format."""
    title, year = parse_movie_title("The Matrix (1999)")
    assert title == "The Matrix"
    assert year == 1999

def test_parse_with_trailing_metadata():
    """Tests formats with extra text at the end."""
    title, year = parse_movie_title("Naked (1993) [BluRay] [1080p]")
    assert title == "Naked"
    assert year == 1993

def test_parse_simple_format():
    """Tests the 'Title YYYY' format."""
    title, year = parse_movie_title("The Kid 1921")
    assert title == "The Kid"
    assert year == 1921

def test_invalid_format_returns_none():
    """Ensures invalid formats return None, None."""
    result = parse_movie_title("Invalid Movie Name Without Year")
    assert result == (None, None)

def test_year_outside_range_is_invalid():
    """Ensures years outside the valid range are ignored."""
    result = parse_movie_title("A Fake Movie 1700")
    assert result == (None, None)