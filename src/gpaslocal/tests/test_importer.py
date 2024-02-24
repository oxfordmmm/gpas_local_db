from sqlalchemy import text

def test_some_database_interaction(test_session):
    # Use test_session directly here to interact with the database
    result = test_session.execute(text("SELECT * FROM owners"))
    assert result.rowcount >= 0