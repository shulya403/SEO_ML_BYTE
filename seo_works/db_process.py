#from .models import WpPosts, WpTermRelationships, WpTerms, WpTermTaxonomy

from .models import WpPosts

#TODO: Get records from WpPosts that is Article, Published and have any term of 'rubrics' or 'post_tag' by WpTermTaxonomy
# filtered by id_post

def Select_wpPosts_in_QS(id_start=0):

    wppost_query = WpPosts.objects.filter(post_status__iexact="publish", post_type__iexact="post", id__gt=id_start).\
        values('post_title', 'post_content', 'post_name', 'post_modified')

    return wppost_query

#if __name__ == "__main__":

print(Select_wpPosts_in_QS().count())