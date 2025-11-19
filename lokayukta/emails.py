from django.template.loader import render_to_string
import bs4
from lokayukta import settings
from uuid import uuid4
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from datetime import date, timedelta

from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import *




def user_signup_send_email(data, to_list):
    print("data",data)
    print("data",data['link'])
    try:
        msg_html = render_to_string('account_signup/user_signup.html',data)
        msg_plain = render_to_string('account_signup/user_signup.txt',data)
        send_mail(
            "Email Verification - Awtomated ",
            msg_plain,
            settings.DEFAULT_FROM_EMAIL,
            to_list,
            html_message=msg_html,
            fail_silently=False,
        )
    except:
        print("Issue with sending signup mail....!!")


def forgot_password_send_email(data, to_list):
    try:
        msg_html = render_to_string('reset_password/reset_password.html',data)
        msg_plain = render_to_string('reset_password/reset_password.txt',data)
        send_mail(
            "Reset Password - Awtomated",
            msg_plain,
            settings.DEFAULT_FROM_EMAIL,
            to_list,
            html_message=msg_html,
            fail_silently=False,
        )
    except:
        print("Issue with sending Reset Password - Awtomated mail....!!")