import rules

from dll.content.models import Review, TeachingModule, Tool, Trend, Content


@rules.predicate
def is_author(user, obj: Content):
    return obj.author == user


@rules.predicate
def is_co_author(user, obj: Content):
    return user in obj.co_authors.all()


@rules.predicate
def review_in_progress(user, obj: Review):
    if obj:
        if obj.status in [Review.NEW, Review.IN_PROGRESS]:
            return True
        elif obj.status in [Review.ACCEPTED, Review.DECLINED]:
            return False


@rules.predicate
def content_review_in_progress(user, obj: Content):
    review = getattr(obj, 'review', None)
    return review_in_progress(user, review)


is_authenticated = rules.is_authenticated
is_bsb_reviewer = rules.is_group_member('BSB-Reviewer')
is_tuhh_reviewer = rules.is_group_member('TUHH-Reviewer')


def check_content_for_review(user, content: Content):
    if is_bsb_reviewer(user) and isinstance(content, TeachingModule):
        return True
    elif is_tuhh_reviewer(user) and (isinstance(content, Tool) or isinstance(content, Trend)):
        return True
    else:
        return False


@rules.predicate
def can_review(user, obj: Review):
    content = obj.content
    return check_content_for_review(user, content)


@rules.predicate
def can_review_content(user, content: Content):
    return check_content_for_review(user, content)


rules.add_perm('content.view_content', is_author | is_co_author | (can_review_content & content_review_in_progress))
rules.add_perm('content.view_tool', is_author | is_co_author | (can_review_content & content_review_in_progress))
rules.add_perm('content.view_trend', is_author | is_co_author | (can_review_content & content_review_in_progress))
rules.add_perm('content.view_teachingmodule',
               is_author | is_co_author | (can_review_content & content_review_in_progress))

rules.add_perm('content.add_content', is_authenticated)
rules.add_perm('content.add_tool', is_authenticated)
rules.add_perm('content.add_trend', is_authenticated)
rules.add_perm('content.add_teachingmodule', is_authenticated)

rules.add_perm('content.change_content', (is_author | is_co_author) & ~content_review_in_progress)
rules.add_perm('content.change_tool', (is_author | is_co_author) & ~content_review_in_progress)
rules.add_perm('content.change_trend', (is_author | is_co_author) & ~content_review_in_progress)
rules.add_perm('content.change_teachingmodule', (is_author | is_co_author) & ~content_review_in_progress)

rules.add_perm('content.delete_content', is_author)
rules.add_perm('content.delete_tool', is_author)
rules.add_perm('content.delete_trend', is_author)
rules.add_perm('content.delete_teachingmodule', is_author)

rules.add_perm('content.change_review', can_review & review_in_progress)
