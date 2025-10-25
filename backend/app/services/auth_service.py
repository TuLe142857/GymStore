from ..utils import MailSender, generate_otp
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import *
from ..errors import BaseAppError
from ..extensions import redis_client
import datetime


class AuthService:
    """
    Note: jwt structure:
    {
        identity/sub: user.id (convert to string),
        additional_claims: {'email': user.email, 'role': user.role.name, 'id': user.id},
    }
    """

    """
            PRIVATE METHODS:
    """
    @staticmethod
    def __generate_access_token(user, fresh=False):
        identity = str(user.id)
        additional_claims = {
            'email': user.email,
            'role': user.role.name,
            'id': user.id
        }
        token = create_access_token(identity=identity, additional_claims=additional_claims, fresh=fresh)
        return token

    @staticmethod
    def __generate_refresh_token(user):
        identity = str(user.id)
        additional_claims = {
            'email': user.email,
            'role': user.role.name,
            'id': user.id
        }
        token = create_refresh_token(identity=identity, additional_claims=additional_claims)
        return token


    """
            REGISTRATION:
    """

    @staticmethod
    def verify(email):
        user = User.query.filter_by(email=email).first()
        if user is not None:
            raise BaseAppError("Email already exists", 400)

        otp = generate_otp()
        res = MailSender.send_registration_email(email, otp, "")
        if not res:
            raise BaseAppError("Something wrong, cannot send email", 500)

        redis_client.set(f"verify:{email}", otp, ex=3600)


    @staticmethod
    def verify_confirm(email, otp):
        key = f"verify:{email}"

        otp_stored_bytes = redis_client.get(key)
        if not otp_stored_bytes:
            raise BaseAppError("OTP expired or not found", 400)

        otp_stored = otp_stored_bytes.decode('utf-8')
        if otp_stored != otp:
            raise BaseAppError("Invalid OTP", 400)

        redis_client.delete(key)
        registration_token = generate_otp(length=10)
        redis_client.set(f"registration_token:{email}", registration_token, ex=3600)
        return registration_token


    @staticmethod
    def register(email, password, full_name, registration_token):
        key = f"registration_token:{email}"
        registration_token_stored_bytes = redis_client.get(key)
        if not registration_token_stored_bytes:
            raise BaseAppError("Registration token expired or not found", 400)

        registration_token_stored = registration_token_stored_bytes.decode('utf-8')

        if registration_token_stored != registration_token:
            raise BaseAppError("Invalid registration token", 400)

        redis_client.delete(key)

        role_customer = Role.query.filter_by(name='CUSTOMER').first()

        if not role_customer:
            raise Exception("CUSTOMER role does not exist")

        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role_customer,
            is_active=True
        )

        new_user_info = UserInfor(
            user=new_user,
            full_name=full_name,
        )

        new_user.user_info = new_user_info

        db.session.add(new_user)
        db.session.commit()

        # generate token if success
        access_token = AuthService.__generate_access_token(new_user, fresh=True)
        refresh_token = AuthService.__generate_refresh_token(new_user)
        return access_token, refresh_token


    @staticmethod
    def login(email, password):
        """
        :return: [access token, refresh token] or [None, None]
        """
        user = User.query.filter_by(email=email).first()
        password_hash = user.password_hash
        if (not user) or (not check_password_hash(password_hash, password)):
            raise BaseAppError("Invalid password or email", 401)

        access_token = AuthService.__generate_access_token(user, fresh=True)
        refresh_token = AuthService.__generate_refresh_token(user)
        return access_token, refresh_token


    @staticmethod
    def refresh_access_token(identity):
        return AuthService.__generate_access_token(identity)


    @staticmethod
    def forgot_password(email):
        user = User.query.filter_by(email=email).first()
        if user is None:
            raise BaseAppError("Email does not exists", 404)

        # generate otp
        otp = generate_otp()
        user.otp = otp
        user.otp_expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
        db.session.commit()

        # send otp via mail
        send_mail_success = MailSender.send_otp(user.email, user.user_info.full_name, otp)
        if not send_mail_success:
            raise BaseAppError("Some thing wrong, cannot send email", 500)


    @staticmethod
    def reset_password(email, otp, password):
        user = User.query.filter_by(email=email).first()
        if user is None:
            raise BaseAppError("Email does not exists", 404)

        if (otp != user.otp) or user.otp_expires_at < datetime.datetime.now(datetime.timezone.utc):
            raise BaseAppError("Invalid OTP", 400)

        user.password_hash = generate_password_hash(password)
        user.otp = None
        user.otp_expires = None
        db.session.commit()


    @staticmethod
    def change_password(identity, new_password, old_password):
        user = User.query.filter_by(id=int(identity)).first()
        if user is None:
            raise BaseAppError("User does not exists", 404)
        if not check_password_hash(user.password_hash, old_password):
            raise BaseAppError("Invalid old password", 400)
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()


    @staticmethod
    def get_profile(identity):
        user = User.query.filter_by(id=int(identity)).first()
        return {
            'email': user.email,
            'name': user.user_info.full_name,
            'gender': user.user_info.gender.name,
            'phone': user.user_info.phone_number,
            'date-of-birth': user.user_info.date_of_birth,
            'address': user.user_info.address
        }


    @staticmethod
    def update_profile(identity, data):
        """
        :param identity: get_jwt_identity()
        :param data: request.get_json()
        """
        user = User.query.filter_by(id=int(identity)).first()
        if user is None:
            raise BaseAppError("User does not exists", 404)

        if "old_password" in data and "new_password" in data:
            old_password = data['old_password']
            if check_password_hash(user.password_hash, old_password):
                new_password = data['new_password']
                user.password_hash = generate_password_hash(new_password)
            else:
                raise BaseAppError("Invalid old password", 400)
        if "full_name" in data:
            user.user_info.full_name = data['full_name']
        if "gender" in data:
            user.user_info.gender = Gender(data['gender'])
        if "phone_number" in data:
            user.user_info.phone_number = data['phone_number']
        if "date_of_birth" in data:
            user.user_info.date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        if "address" in data:
            user.user_info.address = data['address']

        db.session.commit()