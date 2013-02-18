from django.conf.urls.defaults import patterns, include, url
from vodkamartiniarticle.feeds import LatestArticlesFeed
from django.views.decorators.cache import never_cache

urlpatterns = patterns('vodkamartiniarticle.views',
    url(r'^$', 'articles_index', {'page': 1}, name='vodkamartiniarticle_articles_home'),
    url(r'^page-(?P<page>\d+)/$', 'articles_index', name='vodkamartiniarticle_articles_index'),
    url(r'^add/$', 'article_add', name='vodkamartiniarticle_article_add'),
    url(r'^edit/article/(?P<pk>\d+)/$', 'article_edit', name='vodkamartiniarticle_article_edit'),

    # used for ajax testing
    #url(r'^ajax-test/$', 'article_ajax_test', name='vodkamartiniarticle_article_ajax_test'),
    #url(r'^json-test/$', 'article_json_test', name='vodkamartiniarticle_article_json_test'),

    url(r'^(?P<slug>[-\w]+)/$', 'article_detail', name='vodkamartiniarticle_article_detail'),
)

urlpatterns += patterns('',
    #url(r'^latest/feed/$', LatestArticlesFeed(), name='vodkamartiniarticle_feed_latest'),
    # avoid per-site caching of feed during development
    url(r'^latest/feed/$', never_cache(LatestArticlesFeed()), name='vodkamartiniarticle_feed_latest'),
)
