from django.shortcuts import render

# Create your views here.

from .models import WpPosts, WpTermRelationships, WpTermTaxonomy

#TODO: Почистить все записи и в ProcessedPosts
# Привязать теги cat_and_tag_query в ProcessedTermRelationship
#



## __ENTER__

def index(request):

    out = {
       'post_count':  Select_wpPosts_in_QS().count()
    }

    return render(request, template_name="index.html", context=out)

def Select_wpPosts_in_QS(id_start=0):

    wppost_query = WpPosts.objects.filter(post_status__iexact="publish", post_type__iexact="post").\
        values('id', 'post_title', 'post_content', 'post_name', 'post_modified')

    return wppost_query

def Select_terms_wpPostsTermsRel_in_list():

    cat_and_tag_query = WpTermTaxonomy.objects.filter(taxonomy__in=["category", "post_tag"]).values_list("term_taxonomy_id")
    related_articles_query = WpTermRelationships.objects.filter(term_taxonomy_id__in=cat_and_tag_query).values_list('object_id', flat=True).distinct()
    print(len(related_articles_query))

    return related_articles_query