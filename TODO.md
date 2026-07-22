# TODO

- [ ] remove deprecated `namespases` support in `urls.py` (kept in 2.3.1 with a
      DeprecationWarning; drop in the next major once projects are migrated to
      `namespaces`)
- [ ] startapp: add a test asserting the generated urls.py uses `namespaces`
- [ ] drop Python 3.8 support once legacy (non-updatable) instances migrate off
      it; 3.8 is EOL upstream, kept in CI for now. Target: after those instances
      move to 3.9+
