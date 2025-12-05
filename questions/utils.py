from user.utils import award_badge

def check_answer_badges(user):
    answer_count = user.answer_set.count()

    if answer_count >= 10:
        award_badge(user, "Expert Helper")

    if answer_count >= 5:
        award_badge(user, "Contributor")

    if answer_count >= 1:
        award_badge(user, "Beginner Helper")


def check_question_badges(user):
    question_count = user.question_set.count()

    if question_count >= 5:
        award_badge(user, "Deep Thinker")

    if question_count >= 1:
        award_badge(user, "Curious")

def check_answer_like_badges(answer):
    like_count = answer.likes

    if like_count >= 25:
        award_badge(answer.author, "Top Answer")

    if like_count >= 10:
        award_badge(answer.author, "Liked Answer")