import pytest
from flaskcbv.request import Request


class TestRemoteAddress:
    def test_returns_real_ip_header_when_present(self, app):
        with app.test_request_context(
            '/',
            environ_base={'HTTP_X_REAL_IP': '1.2.3.4', 'REMOTE_ADDR': '127.0.0.1'},
        ):
            from flask import request
            assert request.remote_address == '1.2.3.4'

    def test_falls_back_to_remote_addr(self, app):
        with app.test_request_context(
            '/',
            environ_base={'REMOTE_ADDR': '10.0.0.1'},
        ):
            from flask import request
            ## No HTTP_X_REAL_IP header — falls back to remote_addr
            assert request.remote_address == '10.0.0.1'

    def test_real_ip_takes_priority_over_remote_addr(self, app):
        with app.test_request_context(
            '/',
            environ_base={
                'HTTP_X_REAL_IP': '5.6.7.8',
                'REMOTE_ADDR': '192.168.1.1',
            },
        ):
            from flask import request
            assert request.remote_address == '5.6.7.8'
            assert request.remote_address != request.remote_addr
