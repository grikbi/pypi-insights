#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the recommendation APIs."""

import random
import json
import mock
import pytest
from faker import Faker
from src.config.cloud_constants import MIN_CONFIDENCE_SCORE
from starlette.testclient import TestClient

faker = Faker()


class MockHPFScoring(mock.Mock):
    """Mock HPFScoring Class."""

    def __init__(self, *args, **kwargs):
        """Initialize the object."""
        super().__init__(*args, **kwargs)

    def predict(self, input_stack):
        """Predict the stacks."""
        pkg_id_list, missing_pkg = self._map_input_to_package_ids(input_stack)
        if len(pkg_id_list) < len(missing_pkg):
            return [], list(missing_pkg)

        companion_pkg = list()
        for pkg in faker.words(len(pkg_id_list)):
            companion_pkg.append({
                'package_name': pkg,
                'cooccurrence_probability': random.randint(MIN_CONFIDENCE_SCORE, 99),
                'topic_list': faker.words(random.randint(0, 3))
            })
        return companion_pkg, list(missing_pkg)

    def _map_input_to_package_ids(self, input_stack):
        """Filter out identified and missing packages."""
        kwown_packages = {'django', 'flask', 'werkzeug', 'six'}
        id_pkg = input_stack.intersection(kwown_packages)
        return id_pkg, input_stack.difference(id_pkg)


@pytest.fixture(scope='module')
@mock.patch('src.models.predict_model.HPFScoring', new_callable=MockHPFScoring)
def api_client(_request):
    """Create an api client instance."""
    from src.recommendation_service import app
    client = TestClient(app)
    return client


class TestRecommendationService:
    """Test Recommendation Service API endpoints."""

    def test_liveness(self, api_client):
        """Test liveness endpoint."""
        response = api_client.get('/api/v1/liveness')
        resp = response.json()
        assert response is not None
        assert response.status_code == 200
        assert resp is not None
        assert resp == {}

    def test_readiness(self, api_client):
        """Test Readiness endpoint."""
        response = api_client.get('/api/v1/readiness')
        resp = response.json()
        assert response is not None
        assert response.status_code == 200
        assert resp is not None
        assert resp["status"] == "ready"

    def test_companion_recommendation_with_known_stack(self, api_client):
        """Test companion recommendation endpoint with proper stack."""
        payload = [{"package_list": ['django', 'flask']}]
        headers = {'content-type': 'application/json'}
        response = api_client.post('/api/v1/companion_recommendation',
                                   data=json.dumps(payload),
                                   headers=headers)
        resp = response.json()
        assert response is not None
        assert response.status_code == 200
        assert resp is not None
        assert len(resp) > 0
        for pkgs in resp:
            assert not pkgs['missing_packages']
            assert pkgs['ecosystem'] == 'pypi'
            assert pkgs['companion_packages']
            for cmp_pkg in pkgs['companion_packages']:
                assert cmp_pkg['package_name']
                assert cmp_pkg['topic_list'] is not None
                assert cmp_pkg['cooccurrence_probability'] >= MIN_CONFIDENCE_SCORE

    def test_companion_recommendation_with_unknown_stack(self, api_client):
        """Test companion recommendation endpoint with unknown stack."""
        payload = [{"package_list": ['unknown1', 'unknown2']}]
        headers = {'content-type': 'application/json'}
        response = api_client.post('/api/v1/companion_recommendation',
                                   data=json.dumps(payload),
                                   headers=headers)
        resp = response.json()
        assert response is not None
        assert response.status_code == 200
        assert resp is not None
        assert len(resp) > 0
        for pkgs in resp:
            assert pkgs['ecosystem'] == 'pypi'
            assert len(pkgs['missing_packages']) == 2
            assert 'unknown1' in pkgs['missing_packages']
            assert 'unknown2' in pkgs['missing_packages']
            assert not pkgs['companion_packages']

    def test_companion_recommendation_with_known_transitive_stack(self, api_client):
        """Test companion recommendation endpoint with transitive stack."""
        payload = [{"package_list": ['flask'], "transitive_stack": ['click']}]
        headers = {'content-type': 'application/json'}
        response = api_client.post('/api/v1/companion_recommendation',
                                   data=json.dumps(payload),
                                   headers=headers)
        resp = response.json()
        assert response is not None
        assert response.status_code == 200
        assert resp is not None
        assert len(resp) > 0
        for pkgs in resp:
            assert not pkgs['missing_packages']
            assert pkgs['companion_packages']
            assert pkgs['ecosystem'] == 'pypi'
            for cmp_pkg in pkgs['companion_packages']:
                assert cmp_pkg['package_name']
                assert cmp_pkg['package_name'] != payload[0]['transitive_stack'][0]
                assert cmp_pkg['topic_list'] is not None
                assert cmp_pkg['cooccurrence_probability'] >= MIN_CONFIDENCE_SCORE
