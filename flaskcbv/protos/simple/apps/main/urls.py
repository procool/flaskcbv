from flaskcbv.url import Url, make_urls
from .views import mainView

namespaces = make_urls(
    Url('', mainView(), name="main"),
)



