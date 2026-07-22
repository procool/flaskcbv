from flaskcbv.url import Url, include, make_urls

import main.urls

namespaces = make_urls(
    Url('/', include(main.urls.namespaces, namespace='main')),
)

