from ..extensions import mail
from flask import current_app, render_template
from flask_mail import Message

class MailSender:
    @staticmethod
    def send_email(to, subject, template, **kwargs)->bool:
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')

        if not sender:
            sender = current_app.config.get('MAIL_USERNAME')

        msg = Message(
            subject,
            sender=sender,
            recipients=[to]
        )

        msg.html = render_template(template, **kwargs)

        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"MailSender can not send to {to}: {str(e)}")
            return False

    @staticmethod
    def send_otp(to, user_name, otp)->bool:
        return MailSender.send_email(to=to, subject="Xác nhận quên mật ",template='email/otp_mail.html', otp=otp, user_name=user_name)

    @staticmethod
    def send_registration_email(to, otp, confirm_link)->bool:
        return MailSender.send_email(to=to, subject="Xác nhận đăng ký tài khoảng", template='email/registration_mail.html', otp=otp, confirm_ink=confirm_link)
