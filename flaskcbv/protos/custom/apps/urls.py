from flaskcbv.url import Url, include, make_urls

import main.urls

namespases = make_urls(
    Url('/', include(main.urls.namespases, namespace='main')),
)

