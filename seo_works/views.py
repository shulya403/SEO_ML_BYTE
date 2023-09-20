from django.shortcuts import render
#import nltk
import re

# Create your views here.

from .models import WpPosts, WpTermRelationships, WpTermTaxonomy, ProcessedPosts

#TODO: Почистить все записи и в ProcessedPosts
# Привязать теги cat_and_tag_query в ProcessedTermRelationship
#



## __ENTER__

def index(request):

    query_wp_posts_total = Select_wpPosts_in_QS(id_start=0)
    query_wp_posts_filtered = query_wp_posts_total.filter(id__in=Select_terms_wpPostsTermsRel_in_list())

    out = {
       'post_count':  query_wp_posts_total.count(),
       'filtered_by_cat_tag': query_wp_posts_filtered.count()
    }

    return render(request, template_name="index.html", context=out)

def clear_html(request):  #очистка от html-тегов и перенос в рабочую таблицу ProcessedPosts

    count=10

    #что уже есть в таблице ProcessedPosts

    proc_post_present = ProcessedPosts.objects.all().values_list("id_post", flat=True)

    query_wp_posts_total = Select_wpPosts_in_QS(id_start=27430)

    exit_ = list()

    for cursor in query_wp_posts_total:
        print(cursor)
        if cursor['id'] not in proc_post_present:
            clear_text = Clear_text(cursor['post_content'])
            print(cursor['id'], type(cursor['id']))
            target = ProcessedPosts(id_post=cursor['id'], post_title=cursor['post_title'], post_clear_content=clear_text, augmented_content=1, verified=0, x_train=0)
            #target.id_post=cursor['id'],
            #target.post_title=cursor['post_title'],
            #target.post_clear_content=clear_text,
            #target.augmented_content=1,
            #target.verified=0,
            #target.x_train=0

            exit_.append({"Name": cursor['post_title'], "Clear_content": clear_text})
            target.save()


    out = {
        "exit": exit_
    }


    return render(request, template_name="clear_html.html", context=out)

def Clear_text(text_html):
    #exit = nltk.clean_html(text_html)

    cleaner_tags = re.compile(r'(<.*?>|\n)')
    exit = re.sub(cleaner_tags, "", text_html)

    return exit

def Select_wpPosts_in_QS(id_start=0):

    wppost_query = WpPosts.objects.filter(post_status__iexact="publish", post_type__iexact="post").\
        filter(id__gt=id_start).\
        values('id', 'post_title', 'post_content', 'post_name', 'post_modified')

    return wppost_query

#def Select_wpPosts_Filtered(wp_posts, filter_list):

#    return wp_posts.filter(id__in=filter_list)

def Select_terms_wpPostsTermsRel_in_list():

    cat_and_tag_query = WpTermTaxonomy.objects.filter(taxonomy__in=["category", "post_tag"]).values_list("term_taxonomy_id")
    print("cat_terms:", len(cat_and_tag_query))
    post_no_pr_query = WpTermRelationships.objects.\
        filter(term_taxonomy_id=250).\
        values_list('object_id', flat=True).distinct() #список ID пресс-релизов (term_id=250)
    print("ralation всего:", WpTermRelationships.objects.all().count())
    print("posts пресс релизов:", len(post_no_pr_query))
    related_post_query = WpTermRelationships.objects.\
        filter(term_taxonomy_id__in=cat_and_tag_query).\
        values_list('object_id', flat=True).\
        exclude(object_id__in=post_no_pr_query).distinct() #список постов имеющих категорию и тег, кроме пресс-релизов
    print("post выход", len(related_post_query))

    return related_post_query