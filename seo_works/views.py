from django.shortcuts import render
from django.db.models import Q, F, Count
#import nltk
import re
import json

import pandas
from django_pandas.io import read_frame


# Create your views here.

from .models import WpPosts, WpTermRelationships, WpTermTaxonomy, ProcessedPosts, ProcessedTermRelationship, WpTerms

#TODO:
# в json базу
## Изьять статьи с термами "пресс-релизы" и "разное"
## перезалить и посчитать новый term_count
## Очистить все таблицы Processed
## УБРАТЬ все термы кроме категорий и тегов! Привязать теги cat_and_tag_query в ProcessedTermRelationship
## Почистить все записи и в ProcessedPosts
#  Посчитать число вхождения тегов. Предложить коэффициент и его в таблицу, в эксель для аугументации





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

    proc_post_present = ProcessedPosts.objects.all().values_list("id_post", flat=True)  #что уже есть в таблице ProcessedPosts

    query_wp_posts_total = Select_wpPosts_in_QS(id_start=20800).filter(id__in=Select_terms_wpPostsTermsRel_in_list())

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

def Cat_Tag_To_ProcessedTermRelationship(request): # категории и теги из wp в proc для всех proc_post

    proc_post_present = ProcessedPosts.objects.all().values_list("id_post", flat=True) # id post в proc_post
    cat_and_tag_query = WpTermTaxonomy.objects.filter(taxonomy__in=["category", "post_tag"]).values_list("term_taxonomy_id", flat=True) #список term_taxonomy_id"
    print(cat_and_tag_query[:10])

    if len(proc_post_present) > 0:
        wp_cat_tag = WpTermRelationships.objects.filter(object_id__in=proc_post_present) # выборка из исходной таблицы для proc_post_present

        for cursor in proc_post_present:
            wp_cat_tag_post = wp_cat_tag.filter(object_id=cursor)
            for i in wp_cat_tag_post:
                if i.term_taxonomy_id in cat_and_tag_query:
                    if not ProcessedTermRelationship.objects.filter(fk_object_id=cursor, fk_term_taxonomy_id=i.term_taxonomy_id).values_list('id_processed_term_relationship', flat=True):
                       new_record = ProcessedTermRelationship(fk_object_id=cursor, fk_term_taxonomy_id=i.term_taxonomy_id)
                       new_record.save()


    out = {
        "exit": ProcessedTermRelationship.objects.all().values("fk_object_id", "fk_term_taxonomy_id")
    }

    return render(request, template_name="cat_tag_proceeded.html", context=out)

def Select_wpPosts_in_QS(id_start=0):

    wppost_query = WpPosts.objects.filter(post_status__iexact="publish", post_type__iexact="post").\
        filter(id__gt=id_start).\
        values('id', 'post_title', 'post_content', 'post_name', 'post_modified')

    return wppost_query

#def Select_wpPosts_Filtered(wp_posts, filter_list):

#    return wp_posts.filter(id__in=filter_list)

def Select_terms_wpPostsTermsRel_in_list(): #список id постов имеющих категории и теги, но не пресс-релизы

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

#расчет вхождения тегов для аугументации
def Count_term_freq():

    qry = ProcessedTermRelationship.objects.values('fk_term_taxonomy_id').annotate(Count('fk_term_taxonomy_id')).order_by('-fk_term_taxonomy_id__count')

    return qry


#вывод вхождения тегов для аугументации

def count_term(request):

    df_left = read_frame(Count_term_freq())

    df_right = read_frame(WpTerms.objects.filter(term_id__in=df_left.fk_term_taxonomy_id.to_list()))

    df_out = df_left.merge(df_right, left_on='fk_term_taxonomy_id', right_on='term_id')[['fk_term_taxonomy_id', 'fk_term_taxonomy_id__count', 'name']]

    df_out.to_excel("./count_term.xlsx")

    print(df_out)

    out = {

        "terms_count": Count_term_freq()


    }

    return render(request, template_name="count_term.html", context=out)

def JSON_Proceed(request): #данные обеих таблиц в JSON

# Почитать про библиотеку json

    qry_post = ProcessedPosts.objects.all()
    qry_terms = ProcessedTermRelationship.objects.all()

    dict_out = dict()

    for cursor in qry_post:
        dict_out[cursor.id_post] = {
            "title": cursor.post_title,
            "content": cursor.post_clear_content,
            "cat-tag": list(qry_terms.filter(fk_object_id=cursor.id_post).values_list('fk_term_taxonomy_id', flat=True))
        }


    with open('./processed_content.json', 'w', encoding='utf8') as f:
        json.dump(dict_out, f, ensure_ascii=False)

    out = {
        "how_posts": len(dict_out)
    }

    return render(request, template_name="json_gen.html", context=out)