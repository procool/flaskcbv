import pytest
from unittest.mock import patch
from flaskcbv.request import Request


def _req_ctx(app, remote_addr='127.0.0.1', real_ip=None):
    environ = {'REMOTE_ADDR': remote_addr}
    if real_ip is not None:
        environ['HTTP_X_REAL_IP'] = real_ip
    return app.test_request_context('/', environ_base=environ)


class TestRemoteAddressUntrusted:
    def test_returns_remote_addr_when_no_trusted_proxies(self, app):
        ## TRUSTED_PROXIES is empty by default → X-Real-IP is ignored
        with _req_ctx(app, remote_addr='1.2.3.4', real_ip='9.9.9.9'):
            from flask import request
            assert request.remote_address == '1.2.3.4'

    def test_returns_remote_addr_without_real_ip_header(self, app):
        with _req_ctx(app, remote_addr='5.6.7.8'):
            from flask import request
            assert request.remote_address == '5.6.7.8'

    def test_unknown_proxy_not_trusted(self, app):
        ## peer is not in TRUSTED_PROXIES → X-Real-IP ignored
        with patch('flaskcbv.request.settings') as mock_settings:
            mock_settings.TRUSTED_PROXIES = ['10.0.0.1']
            with _req_ctx(app, remote_addr='192.168.1.50', real_ip='8.8.8.8'):
                from flask import request
                assert request.remote_address == '192.168.1.50'


class TestRemoteAddressTrusted:
    def test_real_ip_used_when_proxy_trusted(self, app):
        with patch('flaskcbv.request.settings') as mock_settings:
            mock_settings.TRUSTED_PROXIES = ['127.0.0.1']
            with _req_ctx(app, remote_addr='127.0.0.1', real_ip='203.0.113.5'):
                from flask import request
                assert request.remote_address == '203.0.113.5'

    def test_falls_back_to_remote_addr_when_no_real_ip_header(self, app):
        with patch('flaskcbv.request.settings') as mock_settings:
            mock_settings.TRUSTED_PROXIES = ['127.0.0.1']
            with _req_ctx(app, remote_addr='127.0.0.1'):
                from flask import request
                assert request.remote_address == '127.0.0.1'

    def test_multiple_trusted_proxies(self, app):
        with patch('flaskcbv.request.settings') as mock_settings:
            mock_settings.TRUSTED_PROXIES = ['10.0.0.1', '10.0.0.2']
            with _req_ctx(app, remote_addr='10.0.0.2', real_ip='1.1.1.1'):
                from flask import request
                assert request.remote_address == '1.1.1.1'
