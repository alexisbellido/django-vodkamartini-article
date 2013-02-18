from django.contrib.syndication.views import Feed
from vodkamartiniarticle.models import Article
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.feedgenerator import Atom1Feed


class LatestArticlesFeed(Feed):
    feed_type = Rss201rev2Feed
    title = "Latest Articles Feed"
    link = "/articles/"
    #link = "http://example.com"
    description = "Latest articles on the site"

    def items(self):
        return Article.objects.order_by('-created')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.teaser
