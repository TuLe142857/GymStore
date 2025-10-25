import click
from flask.cli import with_appcontext
import random
import json
import datetime
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
import unicodedata

from ..extensions import db
from ..models import User, Role, UserInfor, Gender


# --- HÀM HELPER SINH DỮ LIỆU (Giữ nguyên của bạn) ---

def gen_name(n, percent_male=0.5):
    with open("uploads/names.json", "r") as file:
        data = json.load(file)

    result = {"male": [], "female": []}

    last_names = [x['name'] for x in data['last_name']]
    last_probs = [x['probability'] for x in data['last_name']]

    male_middle = [x['name'] for x in data['male_middle_name']]
    male_mid_probs = [x['probability'] for x in data['male_middle_name']]
    male_first = [x['name'] for x in data['male_first_name']]
    male_first_probs = [x['probability'] for x in data['male_first_name']]

    female_middle = [x['name'] for x in data['female_middle_name']]
    female_mid_probs = [x['probability'] for x in data['female_middle_name']]
    female_first = [x['name'] for x in data['female_first_name']]
    female_first_probs = [x['probability'] for x in data['female_first_name']]

    n_male = int(n * percent_male)
    n_female = n - n_male


    rand_male_last = random.choices(last_names, weights=last_probs, k=n_male)
    rand_male_middle = random.choices(male_middle, weights=male_mid_probs, k=n_male)
    rand_male_first = random.choices(male_first, weights=male_first_probs, k=n_male)

    for t in zip(rand_male_last, rand_male_middle, rand_male_first):
        result['male'].append(" ".join(t))


    rand_female_last = random.choices(last_names, weights=last_probs, k=n_female)
    rand_female_middle = random.choices(female_middle, weights=female_mid_probs, k=n_female)
    rand_female_first = random.choices(female_first, weights=female_first_probs, k=n_female)

    for t in zip(rand_female_last, rand_female_middle, rand_female_first):
        result['female'].append(" ".join(t))

    return result["male"], result["female"]


def gen_email(name, user_id):
    def remove_vietnamese_tone(text: str) -> str:
        normalized = unicodedata.normalize('NFD', text)
        without_tone = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return without_tone.lower()
    normalized_name = " ".join(remove_vietnamese_tone(name).split())
    return f"{normalized_name}{user_id}@fakemail.com"


def gen_address():
    """Tạo địa chỉ giả định."""
    streets = ["Lê Lợi", "Nguyễn Huệ", "Trần Hưng Đạo", "Hai Bà Trưng", "Phạm Ngũ Lão", "Điện Biên Phủ"]
    wards = ["Phường Bến Nghé", "Phường Đa Kao", "Phường Cầu Ông Lãnh", "Phường Tân Định"]
    districts = ["Quận 1", "Quận 3", "Quận Bình Thạnh", "Quận Phú Nhuận"]
    city = "TP. Hồ Chí Minh"
    return f"{random.randint(1, 500)} {random.choice(streets)}, {random.choice(wards)}, {random.choice(districts)}, {city}"


def gen_phone_number():
    """Tạo số điện thoại giả định (định dạng Việt Nam)."""
    # Các đầu số phổ biến
    prefixes = ['090', '091', '098', '097', '096', '086', '088', '089', '032', '033', '034', '035', '036', '037', '038',
                '039', '070', '079', '077', '076', '078', '056', '058', '059']
    return random.choice(prefixes) + "".join([str(random.randint(0, 9)) for _ in range(7)])


def gen_dob(age_range = (18, 30)):
    today = datetime.date.today()
    start_date = today.replace(year=today.year - age_range[1])
    end_date = today.replace(year=today.year - age_range[0])
    total_days = (end_date - start_date).days
    random_days = random.randint(0, total_days)
    return start_date + datetime.timedelta(days=random_days)


# --- HÀM HELPER DB ---

def get_or_create_role(role_name):
    """Tìm hoặc tạo Role trong DB."""
    role = db.session.query(Role).filter_by(name=role_name).first()
    if not role:
        click.echo(f"  > Role '{role_name}' not found. Creating...")
        role = Role(name=role_name)
        db.session.add(role)
        try:
            # Commit ngay để Role có ID và các user sau có thể dùng
            db.session.commit()
            click.echo(f"  > Role '{role_name}' created successfully.")
        except IntegrityError:  # Trường hợp race condition (hiếm)
            db.session.rollback()
            role = db.session.query(Role).filter_by(name=role_name).first()
            click.echo(f"  > Role '{role_name}' already exists (race condition).")
        except Exception as e:
            db.session.rollback()
            click.echo(f"  > Error creating role '{role_name}': {e}", err=True)
            return None  # Trả về None nếu không tạo được role
    return role


# --- COMMAND CHÍNH ---

@click.command("generate-users", short_help="Generate fake user data.")
@click.option("--n", default=100, type=int, help="Number of users to generate.")
@click.option("--password", default="123456", help="Password for all generated users.")
@click.option("--clear", is_flag=True, help="Clear UserInfor and User tables before generating.")
@with_appcontext
def generate_users(n, password, clear):

    if clear:
        click.echo("Clearing UserInfor and User tables...")
        try:
            # Xóa UserInfor trước do khóa ngoại
            num_infor_deleted = db.session.query(UserInfor).delete()
            num_user_deleted = db.session.query(User).delete()
            db.session.commit()
            click.echo(f"  > Deleted {num_infor_deleted} UserInfor records.")
            click.echo(f"  > Deleted {num_user_deleted} User records.")
            click.echo("Tables cleared successfully.")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error clearing tables: {e}", err=True)
            return  # Dừng nếu không xóa được

    # Lấy hoặc tạo Role 'USER'
    user_role = get_or_create_role('USER')
    admin_role = get_or_create_role('ADMIN')  # Đảm bảo có cả role ADMIN

    if not user_role:
        click.echo("Error: Could not get or create 'USER' role. Aborting.", err=True)
        return

    click.echo(f"Generating {n} users with password '{password}'...")

    # Tạo danh sách tên trước
    male_names, female_names = gen_name(n)
    if not male_names and not female_names:
        click.echo("Error generating names. Aborting.", err=True)
        return

    # Hash password một lần
    hashed_password = generate_password_hash(password)

    created_count = 0
    error_count = 0
    skipped_name_count = 0

    # Tạo admin user nếu chưa có
    admin_exists = db.session.query(User.id).filter_by(email='admin@gymstore.com').first()
    if not admin_exists:
        click.echo("Creating admin user 'admin@gymstore.com'...")
        admin_user = User(
            email='admin@gymstore.com',
            password_hash=generate_password_hash("admin123"),  # Mật khẩu riêng cho admin
            role=admin_role,
            is_active=True
        )
        admin_info = UserInfor(
            user=admin_user,  # Liên kết trực tiếp object
            full_name="Admin GymStore",
            gender=Gender.OTHER,
            phone_number="0123456789",  # SĐT mẫu
            date_of_birth=datetime.date(1990, 1, 1),  # Ngày sinh mẫu
            address=gen_address()
        )
        db.session.add_all([admin_user, admin_info])
        try:
            db.session.commit()
            click.echo("  > Admin user created.")
        except Exception as e:
            db.session.rollback()
            click.echo(f"  > Error creating admin user: {e}", err=True)

    click.echo(f"Starting user generation loop for {n} users...")
    user_id_counter = db.session.query(db.func.max(User.id)).scalar() or 0  # Lấy ID lớn nhất để tạo email unique

    for i in range(n):
        user_id_counter += 1  # Tăng ID giả định cho email

        # Chọn giới tính ngẫu nhiên và lấy tên tương ứng
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        full_name = None

        try:
            if gender == Gender.MALE and male_names:
                full_name = male_names.pop(random.randrange(len(male_names)))  # Lấy ngẫu nhiên và xóa
            elif gender == Gender.FEMALE and female_names:
                full_name = female_names.pop(random.randrange(len(female_names)))
            else:  # Nếu hết tên cho giới tính đó, thử lấy giới tính còn lại
                if male_names:
                    full_name = male_names.pop(random.randrange(len(male_names)))
                    gender = Gender.MALE
                elif female_names:
                    full_name = female_names.pop(random.randrange(len(female_names)))
                    gender = Gender.FEMALE
                else:
                    click.echo(f"  > Warning: Ran out of names at index {i}. Stopping.", err=True)
                    skipped_name_count += (n - i)
                    break  # Hết tên thì dừng
        except IndexError:
            click.echo(f"  > Warning: Index error while getting name at index {i}. Stopping.", err=True)
            skipped_name_count += (n - i)
            break

        if not full_name:  # Vẫn kiểm tra lại nếu pop bị lỗi
            skipped_name_count += 1
            continue

        # Tạo các thông tin khác
        email = gen_email(full_name, user_id_counter)
        phone = gen_phone_number()
        dob = gen_dob()
        address = gen_address()

        # Tạo object User và UserInfor
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role=user_role,  # Gán object Role
            is_active=True  # Mặc định active
        )
        new_user_info = UserInfor(
            user=new_user,  # Quan trọng: Liên kết trực tiếp object User
            full_name=full_name,
            gender=gender,
            phone_number=phone,
            date_of_birth=dob,
            address=address
        )

        # Thêm vào session và commit (xử lý lỗi trùng lặp)
        db.session.add(new_user)
        # UserInfor tự động được thêm do cascade khi add User (nếu relationship cấu hình đúng)
        # db.session.add(new_user_info) # Có thể không cần dòng này nếu cascade="all"

        try:
            db.session.commit()
            created_count += 1
            if (i + 1) % 50 == 0:  # In log mỗi 50 users
                click.echo(f"  > Created user {created_count}/{n}...")
        except IntegrityError as e:
            db.session.rollback()  # Rất quan trọng: rollback khi lỗi
            click.echo(
                f"  > Skipping user '{full_name}' due to DB integrity error (likely duplicate email/phone): {e.orig}",
                err=True)
            error_count += 1
            user_id_counter -= 1  # Giảm counter lại vì user này không được tạo
        except Exception as e:
            db.session.rollback()
            click.echo(f"  > Unexpected error creating user '{full_name}': {e}", err=True)
            error_count += 1
            user_id_counter -= 1  # Giảm counter

    click.echo("\n--- User Generation Summary ---")
    click.echo(f"Target users:          {n}")
    click.echo(f"Successfully created:  {created_count}")
    click.echo(f"Skipped (out of names):{skipped_name_count}")
    click.echo(f"Skipped (DB errors):   {error_count}")
    click.echo("-----------------------------")


