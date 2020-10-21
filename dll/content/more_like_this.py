import pysolr
from environs import Env
from constance import config
from dll.content.models import Content


def more_like_this(content):
    content_str = f"content.{content.type}.{content.pk}".replace("-", "")

    def mlt_append(use: bool, name: str, boost: float, mlt_fl, mlt_qf):
        if use:
            mlt_fl.append(name)
            mlt_qf.append(f"text^{str(boost)}")
        return mlt_fl, mlt_qf

    parameter_list = [
        {
            "use": config.MORE_LIKE_THIS_USE_TEXT,
            "name": "text",
            "boost": config.MORE_LIKE_THIS_BOOST_TEXT,
        },
        {
            "use": config.MORE_LIKE_THIS_USE_NAME,
            "name": "name",
            "boost": config.MORE_LIKE_THIS_BOOST_NAME,
        },
        {
            "use": config.MORE_LIKE_THIS_USE_TEASER,
            "name": "teaser",
            "boost": config.MORE_LIKE_THIS_BOOST_TEASER,
        },
        {
            "use": config.MORE_LIKE_THIS_USE_ADDITIONAL_INFO,
            "name": "additional_info",
            "boost": config.MORE_LIKE_THIS_BOOST_ADDITIONAL_INFO,
        },
        {
            "use": config.MORE_LIKE_THIS_USE_TAGS,
            "name": "tags",
            "boost": config.MORE_LIKE_THIS_BOOST_TAGS,
        },
        {
            "use": config.MORE_LIKE_THIS_USE_AUTHORS,
            "name": "authors",
            "boost": config.MORE_LIKE_THIS_BOOST_AUTHORS,
        },
        {
            "use": config.MORE_LIKE_THIS_USE_SUBJECTS,
            "name": "subjects",
            "boost": config.MORE_LIKE_THIS_BOOST_SUBJECTS,
        },
    ]

    mlt_fl = []
    mlt_qf = []
    for parameter in parameter_list:
        mlt_fl, mlt_qf = mlt_append(
            parameter["use"], parameter["name"], parameter["boost"], mlt_fl, mlt_qf
        )
    mlt_fl = ",".join(mlt_fl)
    mlt_qf = " ".join(mlt_qf)

    env = Env()
    solr = pysolr.Solr(
        f"http://{env.str('SOLR_HOSTNAME')}:8983/solr/dll-default", always_commit=True
    )
    response = solr.search(
        q=f"id:{content_str}",
        **{
            "fl": "*,score",
            # Common Parameters for MoreLikeThis
            "mlt.fl": mlt_fl,
            "mlt.mintf": 1,
            "mlt.mindf": 1,
            # "mlt.maxdf": 1,
            "mlt.minwl": 4,
            # "mlt.maxwl": 25,
            "mlt.maxqt": 1000,
            "mlt.maxntp": 100,
            "mlt.boost": "true",
            "mlt.qf": mlt_qf,
            # Parameters for the MoreLikeThisComponent
            "mlt": "true",
            "mlt.count": config.MORE_LIKE_THIS_COUNT,
            # Parameters for the MoreLikeThisHandler
            "mlt.match.include": "false",
            "mlt.match.offset": 0,
            "mlt.interestingTerms": "none",  # "none" / "details"
        },
    )

    try:
        raw = response.raw_response
        docs = raw["moreLikeThis"][content_str]["docs"]
        result_list = [{"django_id": d["django_id"], "score": d["score"]} for d in docs]

        result_list = sorted(result_list, key=lambda k: k["score"])

        result_score_cutoff = [
            result["django_id"]
            for result in result_list
            if result["score"] > config.MORE_LIKE_THIS_SCORE_CUTOFF
        ]
        mlt_polymorphic_qs = Content.objects.filter(pk__in=result_score_cutoff)
        mlt_real_qs = mlt_polymorphic_qs.get_real_instances()
    except Exception as e:
        print(e)
        return None

    return mlt_real_qs
