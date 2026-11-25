from cardgame import server


def test_play_returns_html_with_new_match():
    response = server.app.test_client().get("/play")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert "New match" in response.get_data(as_text=True)
