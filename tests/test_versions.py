from http import HTTPStatus


def test_versions(client):
    resp = client.test_client().get('/versions')

    assert resp.status_code == HTTPStatus.OK
    assert resp.json['success'] is True

    assert 'versions' in resp.json
    assert len(resp.json['versions']) > 1
