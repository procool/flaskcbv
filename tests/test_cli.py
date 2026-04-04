import os
import string
import pytest
from flaskcbv.scripts.common import CommonMixin
from flaskcbv.scripts.commands.initproject import cmdInitProject
from flaskcbv.scripts.commands.startapp import cmdStartApp
from flaskcbv.scripts.cliargs import CliArgs


class _CliInitProject(cmdInitProject, CliArgs):
    pass


class _CliStartApp(cmdStartApp, CliArgs):
    pass


class TestTokenGen:
    def test_default_length(self):
        token = CommonMixin.token_gen()
        assert len(token) == 6

    def test_custom_length(self):
        token = CommonMixin.token_gen(size=20)
        assert len(token) == 20

    def test_uses_uppercase_and_digits_only(self):
        allowed = set(string.ascii_uppercase + string.digits)
        for _ in range(20):
            token = CommonMixin.token_gen(size=10)
            assert set(token).issubset(allowed)

    def test_static_token_is_cached(self):
        ## static_token() returns the same value for the same class
        t1 = CommonMixin.static_token(size=8)
        t2 = CommonMixin.static_token(size=8)
        assert t1 == t2


class TestGenToken:
    def test_length_matches_requested(self):
        token = cmdInitProject.gen_token(50)
        assert len(token) == 50

    def test_minimum_production_length(self):
        ## SECRET_KEY is generated with size=50 — verify it's long enough
        token = cmdInitProject.gen_token(50)
        assert len(token) >= 50

    def test_token_is_string(self):
        token = cmdInitProject.gen_token(10)
        assert isinstance(token, str)

    def test_tokens_are_unique(self):
        ## With a large enough token, two calls should produce different results
        tokens = {cmdInitProject.gen_token(32) for _ in range(10)}
        assert len(tokens) > 1


class TestGetCliCommands:
    def test_initproject_registered(self):
        d = _CliInitProject()
        cmds = d.get_cli_commands()
        assert 'initproject' in cmds

    def test_initproject_is_callable(self):
        d = _CliInitProject()
        cmds = d.get_cli_commands()
        assert callable(cmds['initproject'])


class TestStartApp:
    def test_startapp_registered(self):
        d = _CliStartApp()
        assert 'startapp' in d.get_cli_commands()

    def test_startapp_is_callable(self):
        d = _CliStartApp()
        assert callable(d.get_cli_commands()['startapp'])

    def test_creates_expected_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = _CliStartApp()
        d._startapp_name = 'blog'
        d.get_cli_commands()['startapp']()

        assert (tmp_path / 'apps' / 'blog' / '__init__.py').exists()
        assert (tmp_path / 'apps' / 'blog' / 'views.py').exists()
        assert (tmp_path / 'apps' / 'blog' / 'urls.py').exists()
        assert (tmp_path / 'apps' / 'blog' / 'templates' / 'blog' / 'index.tpl').exists()

    def test_views_contains_app_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = _CliStartApp()
        d._startapp_name = 'news'
        d.get_cli_commands()['startapp']()

        content = (tmp_path / 'apps' / 'news' / 'views.py').read_text()
        assert 'news' in content

    def test_raises_without_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = _CliStartApp()
        d._startapp_name = None
        with pytest.raises(Exception, match='startapp'):
            d.get_cli_commands()['startapp']()

    def test_raises_if_dir_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'apps' / 'shop').mkdir(parents=True)
        d = _CliStartApp()
        d._startapp_name = 'shop'
        with pytest.raises(Exception, match='already exists'):
            d.get_cli_commands()['startapp']()


class TestInitProject:
    def test_build_proto_creates_file(self, tmp_path, monkeypatch):
        ## Change CWD to tmp_path so os.path.abspath() resolves there
        monkeypatch.chdir(tmp_path)

        class Dummy(cmdInitProject):
            def get_cli_commands(self):
                return {}

        d = Dummy()
        d.build_proto('settings/__init__.py', WEB=str(tmp_path), APPS=str(tmp_path / 'apps'), SECRET_KEY='x' * 50)
        assert (tmp_path / 'settings' / '__init__.py').exists()

    def test_build_proto_raises_if_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        target = tmp_path / 'settings'
        target.mkdir()
        (target / '__init__.py').write_text('# existing')

        class Dummy(cmdInitProject):
            def get_cli_commands(self):
                return {}

        d = Dummy()
        with pytest.raises(Exception, match='allready exist'):
            d.build_proto('settings/__init__.py', WEB=str(tmp_path), APPS=str(tmp_path), SECRET_KEY='x' * 50)
