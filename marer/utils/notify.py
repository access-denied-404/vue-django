import warnings

from django.conf import settings

from marer.models import Issue, User, IssueClarification, \
    IssueClarificationMessage
from marer.models.issue import IssueProposeDocument


def _get_default_manager():
    return User.objects.get(id=settings.DEFAULT_MANAGER_ID)


def notify_user_about_manager_created_issue_for_user(issue: Issue):
    user_manager = issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    user = issue.user
    # менеджер создал заявку, уведомить клиента
    user.email_user(
        subject="Ваш менеджер создал Вам новую заявку",
        html_template_filename='mail/events_for_send_to_user/manager_created_new_issue_for_user.html',
        context=dict(
            manager_full_name=user_manager.__str__(),
            new_issue_id=issue.id,
            new_issue_number=issue.humanized_id,
            finance_product=issue.get_product().humanized_name,
            issuer_short_name=issue.issuer_short_name,
        )
    )


def notify_user_manager_about_user_created_issue(issue: Issue):
    user_manager = issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    # клиент создал заявку, уведомить менеджера
    user_manager.email_user(
        subject="Новая заявка от клиента",
        html_template_filename='mail/events_for_send_to_user_manager/user_created_new_issue.html',
        context=dict(
            user_full_name=issue.user.__str__(),
            new_issue_id=issue.id,
            new_issue_number=issue.humanized_id,
            finance_product=issue.get_product().humanized_name,
            issuer_short_name=issue.issuer_short_name,
        )
    )


def notify_user_manager_about_user_sign_document(document: IssueProposeDocument):
    issue = document.issue
    user_manager = issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    # клиент создал заявку, уведомить менеджера
    user_manager.email_user(
        subject="Клиент подписал документ",
        html_template_filename='mail/events_for_send_to_user_manager/user_sign_document.html',
        context=dict(
            user_full_name=issue.user.__str__(),
            new_issue_id=issue.id,
            new_issue_number=issue.humanized_id,
            finance_product=issue.get_product().humanized_name,
            issuer_short_name=issue.issuer_short_name,
            document_name = document.name,
        )
    )


def notify_user_about_manager_updated_issue_for_user(issue: Issue):
    # DISABLED
    # user_manager = issue.user.manager
    # if user_manager is None:
    #     user_manager = _get_default_manager()
    #
    # user = issue.user
    # # менеджер пользователя изменил заявку, уведомить клиента
    # user.email_user(
    #     subject="Ваш менеджер изменил Вашу заявку",
    #     html_template_filename='mail/events_for_send_to_user/manager_updated_issue_for_user.html',
    #     context=dict(
    #         manager_full_name=user_manager.__str__(),
    #         issue_id=issue.id,
    #         issue_number=issue.humanized_id,
    #         finance_product=issue.get_product().humanized_name,
    #         issuer_short_name=issue.issuer_short_name,
    #     )
    # )
    pass


def notify_user_manager_about_user_updated_issue(issue: Issue):
    user_manager = issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    # клиент создал заявку, уведомить менеджера
    user_manager.email_user(
        subject="Клиент изменил заявку",
        html_template_filename='mail/events_for_send_to_user_manager/user_updated_issue.html',
        context=dict(
            user_full_name=issue.user.__str__(),
            issue_id=issue.id,
            issue_number=issue.humanized_id,
            finance_product=issue.get_product().humanized_name,
            issuer_short_name=issue.issuer_short_name,
        )
    )


def notify_fo_managers_about_issue_proposed_to_banks(proposes: list):
    if len(proposes) == 0:
        return
    managers_fo_proposes = {}
    issue = proposes[0].issue
    for propose in proposes:
        mgr_id = propose.finance_org.manager_id
        if not mgr_id:
            warnings.warn('No manager for FO #{org_id} got notify of new issue FO propose'.format(
                org_id=propose.finance_org.id
            ))
            continue
        mgr_proposes = managers_fo_proposes.get(mgr_id, [])
        if propose not in mgr_proposes:
            mgr_proposes.append(propose)
            managers_fo_proposes[mgr_id] = mgr_proposes
    for fo_manager_id in managers_fo_proposes:
        # клиент отправил заявку в банки, уведомить менеджера по банкам
        fo_manager = User.objects.get(id=fo_manager_id)
        fo_manager.email_user(
            subject="Клиент отправил заявку в ваши банки",
            html_template_filename='mail/events_for_send_to_fo_manager/issue_proposed_to_fo.html',
            context=dict(
                user_full_name=issue.user.__str__(),
                issue_id=issue.id,
                issue_number=issue.humanized_id,
                proposes=managers_fo_proposes[fo_manager_id],
                finance_product=issue.get_product().humanized_name,
                issuer_short_name=issue.issuer_short_name,
            )
        )


def notify_user_about_issue_proposed_to_banks(proposes: list):
    # DISABLED
    # # клиентский менеджер отправил заявку в банки, уведомить пользователя
    # if len(proposes) == 0:
    #     return
    #
    # issue = proposes[0].issue
    # issue.user.email_user(
    #     subject="Ваш менеджер предложил Вашу заявку в банки",
    #     html_template_filename='mail/events_for_send_to_user/user_manager_proposed_issue_to_fo.html',
    #     context=dict(
    #         issue_id=issue.id,
    #         issue_number=issue.humanized_id,
    #         proposes=proposes,
    #         finance_product=issue.get_product().humanized_name,
    #         issuer_short_name=issue.issuer_short_name,
    #     )
    # )
    pass


def notify_user_manager_about_issue_proposed_to_banks(proposes: list):
    # клиент отправил заявку в банки, уведомить менеджера пользователя
    if len(proposes) == 0:
        return

    issue = proposes[0].issue
    user_manager = issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    user_manager.email_user(
        subject="Пользователь предложил заявку в банки",
        html_template_filename='mail/events_for_send_to_user_manager/user_proposed_issue_to_fo.html',
        context=dict(
            user_full_name=issue.user.__str__(),
            issue_id=issue.id,
            issue_number=issue.humanized_id,
            proposes=proposes,
            finance_product=issue.get_product().humanized_name,
            issuer_short_name=issue.issuer_short_name,
        )
    )


def notify_about_user_created_clarification(clarification: IssueClarification):
    # notify user manager and fo manager

    # DISABLED
    # user_manager = clarification.propose.issue.user.manager
    # if user_manager is None:
    #     user_manager = _get_default_manager()
    #
    # user_manager.email_user(
    #     subject="Пользователь создал новый дозапрос по заявке",
    #     html_template_filename='mail/events_for_send_to_user/.html',
    #     context=dict(
    #         # user_full_name=propose.issue.user.__str__(),
    #         # issue_id=propose.issue.id,
    #         # issue_number=propose.issue.humanized_id,
    #         # finance_product=propose.issue.get_product().humanized_name,
    #         # issuer_short_name=propose.issue.issuer_short_name,
    #     )
    # )

    # if not clarification.propose.finance_org.manager_id:
    #     warnings.warn('No manager for FO #{org_id} got notify of clarification for propose #{propose_id}'.format(
    #         org_id=clarification.propose.finance_org.id,
    #         propose_id=clarification.propose_id,
    #     ))
    # else:
    #     clarification.propose.finance_org.manager.email_user(
    #         subject="Пользователь создал новый дозапрос по заявке",
    #         html_template_filename='mail/events_for_send_to_fo_manager/user_created_clarification.html',
    #         context=dict(
    #             user_full_name=clarification.propose.issue.user.__str__(),
    #             issue_id=clarification.propose.issue.id,
    #             issue_number=clarification.propose.issue.humanized_id,
    #             finance_product=clarification.propose.issue.get_product().humanized_name,
    #             issuer_short_name=clarification.propose.issue.issuer_short_name,
    #             finance_org_name=clarification.propose.finance_org.name,
    #             clarification_id=clarification.id,
    #         )
    #     )

    warnings.warn('Clarification {} is saved but nobody notified'.format(clarification.id))


def notify_about_user_manager_created_clarification(clarification: IssueClarification):
    # notify user and fo manager

    # DISABLED
    # user = clarification.propose.issue.user
    # user.email_user(
    #     subject="Менеджер добавил дозапрос по Вашей заявке в банке",
    #     html_template_filename='mail/events_for_send_to_user/user_manager_created_clarification.html',
    #     context=dict(
    #         clarification_id=clarification.id,
    #         issue_id=clarification.propose.issue.id,
    #         issue_number=clarification.propose.issue.humanized_id,
    #         finance_product=clarification.propose.issue.get_product().humanized_name,
    #         finance_org_name=clarification.propose.finance_org.name,
    #         issuer_short_name=clarification.propose.issue.issuer_short_name,
    #     )
    # )

    if not clarification.propose.finance_org.manager_id:
        warnings.warn('No manager for FO #{org_id} got notify of clarification for propose #{propose_id}'.format(
            org_id=clarification.propose.finance_org.id,
            propose_id=clarification.propose_id,
        ))
    else:
        clarification.propose.finance_org.manager.email_user(
            subject="Менеджер клиента создал дозапрос по заявке в Ваш банк",
            html_template_filename='mail/events_for_send_to_fo_manager/user_manager_created_clarification.html',
            context=dict(
                issue_id=clarification.propose.issue.id,
                issue_number=clarification.propose.issue.humanized_id,
                finance_product=clarification.propose.issue.get_product().humanized_name,
                issuer_short_name=clarification.propose.issue.issuer_short_name,
                finance_org_name=clarification.propose.finance_org.name,
                clarification_id=clarification.id,
            )
        )


def notify_about_fo_manager_created_clarification(clarification: IssueClarification):
    # менеджер банка создал дозапрос, уведомить клиента

    user = clarification.propose.issue.user
    user.email_user(
        subject="Менеджер банка создал дозапрос по Вашей заявке",
        html_template_filename='mail/events_for_send_to_user/fo_manager_created_clarification.html',
        context=dict(
            clarification_id=clarification.id,
            issue_id=clarification.propose.issue.id,
            issue_number=clarification.propose.issue.humanized_id,
            finance_product=clarification.propose.issue.get_product().humanized_name,
            finance_org_name=clarification.propose.finance_org.name,
            issuer_short_name=clarification.propose.issue.issuer_short_name,
        )
    )

    user_manager = clarification.propose.issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    user_manager.email_user(
        subject="Менеджер банка создал дозапрос по заявке Вашего пользователя",
        html_template_filename='mail/events_for_send_to_user/fo_manager_created_clarification.html',
        context=dict(
            clarification_id=clarification.id,
            issue_number=clarification.propose.issue.humanized_id,
            issue_id=clarification.propose.issue.id,
            finance_product=clarification.propose.issue.get_product().humanized_name,
            finance_org_name=clarification.propose.finance_org.name,
            issuer_short_name=clarification.propose.issue.issuer_short_name,
        )
    )


def notify_about_user_adds_message(msg: IssueClarificationMessage):
    # notify fo manager and user manager

    # DISABLED
    # user_manager = msg.clarification.propose.issue.user.manager
    # if user_manager is None:
    #     user_manager = _get_default_manager()
    #
    # user_manager.email_user(
    #     subject="Пользователь добавил сообщение по дозапросу в заявке",
    #     html_template_filename='mail/events_for_send_to_user/.html',
    #     context=dict(
    #         # user_full_name=propose.issue.user.__str__(),
    #         # issue_id=propose.issue.id,
    #         # issue_number=propose.issue.humanized_id,
    #         # finance_product=propose.issue.get_product().humanized_name,
    #         # issuer_short_name=propose.issue.issuer_short_name,
    #     )
    # )

    if not msg.clarification.propose.finance_org.manager_id:
        warnings.warn('No manager for FO #{org_id} got notify of clarification for propose #{propose_id}'.format(
            org_id=msg.clarification.propose.finance_org.id,
            propose_id=msg.clarification.propose_id,
        ))
    else:
        msg.clarification.propose.finance_org.manager.email_user(
            subject="Менеджер клиента оставил новое сообщение по дозапросу к заявке в Ваш банк",
            html_template_filename='mail/events_for_send_to_fo_manager/user_added_clarification_message.html',
            context=dict(
                user_full_name=msg.clarification.propose.issue.user.__str__(),
                issue_id=msg.clarification.propose.issue.id,
                issue_number=msg.clarification.propose.issue.humanized_id,
                finance_product=msg.clarification.propose.issue.get_product().humanized_name,
                issuer_short_name=msg.clarification.propose.issue.issuer_short_name,
                finance_org_name=msg.clarification.propose.finance_org.name,
                clarification_id=msg.clarification.id,
            )
        )


def notify_about_user_manager_adds_message(msg: IssueClarificationMessage):
    # notify user and fo manager

    # DISABLED
    # user = msg.clarification.propose.issue.user
    # user.email_user(
    #     subject="Ваш менеджер добавил сообщение по дозапросу к заявке в банк",
    #     html_template_filename='mail/events_for_send_to_user/.html',
    #     context=dict(
    #         # issue_id=propose.issue.id,
    #         # issue_number=propose.issue.humanized_id,
    #         # finance_product=propose.issue.get_product().humanized_name,
    #         # finance_org_name=propose.finance_org.name,
    #         # propose_id=propose.id,
    #         # issuer_short_name=propose.issue.issuer_short_name,
    #     )
    # )

    if not msg.clarification.propose.finance_org.manager_id:
        warnings.warn('No manager for FO #{org_id} got notify of clarification for propose #{propose_id}'.format(
            org_id=msg.clarification.propose.finance_org.id,
            propose_id=msg.clarification.propose_id,
        ))
    else:
        msg.clarification.propose.finance_org.manager.email_user(
            subject="Менеджер клиента добавил сообщение по дозапросу к заявке в Ваш банк",
            html_template_filename='mail/events_for_send_to_fo_manager/user_manager_added_clarification_message.html',
            context=dict(
                issue_id=msg.clarification.propose.issue.id,
                issue_number=msg.clarification.propose.issue.humanized_id,
                finance_product=msg.clarification.propose.issue.get_product().humanized_name,
                issuer_short_name=msg.clarification.propose.issue.issuer_short_name,
                finance_org_name=msg.clarification.propose.finance_org.name,
                clarification_id=msg.clarification.id,
            )
        )


def notify_about_fo_manager_adds_message(msg: IssueClarificationMessage):
    # notify user and user manager

    user = msg.clarification.propose.issue.user
    user.email_user(
        subject="Менеджер банка добавил сообщение по дозапросу к заявке в банк",
        html_template_filename='mail/events_for_send_to_user/fo_manager_added_clarification_message.html',
        context=dict(
            clarification_id=msg.clarification.id,
            issue_id=msg.clarification.propose.issue.id,
            issue_number=msg.clarification.propose.issue.humanized_id,
            finance_product=msg.clarification.propose.issue.get_product().humanized_name,
            finance_org_name=msg.clarification.propose.finance_org.name,
            issuer_short_name=msg.clarification.propose.issue.issuer_short_name,
        )
    )

    user_manager = msg.clarification.propose.issue.user.manager
    if user_manager is None:
        user_manager = _get_default_manager()

    user_manager.email_user(
        subject="Менеджер банка добавил сообщение по дозапросу к заявке в банк",
        html_template_filename='mail/events_for_send_to_user/fo_manager_added_clarification_message.html',
        context=dict(
            clarification_id=msg.clarification.id,
            issue_number=msg.clarification.propose.issue.humanized_id,
            issue_id=msg.clarification.propose.issue.id,
            finance_product=msg.clarification.propose.issue.get_product().humanized_name,
            finance_org_name=msg.clarification.propose.finance_org.name,
            issuer_short_name=msg.clarification.propose.issue.issuer_short_name,
        )
    )
