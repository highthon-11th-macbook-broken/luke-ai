from faker import Faker
import pandas as pd
import random

# 한국어 기반 Faker
fake = Faker('ko_KR')

# 비밀번호 패턴 생성 함수
def generate_password_patterns():
    patterns = [
        "qwerty123", "pass1234", "sunny97!", "1234lee",
        "mk8908@!", "choi!pw", "hello2020", "test@321",
        "abc123!", "mypw!456", "pw123456", "1q2w3e4r"
    ]
    return ','.join(random.sample(patterns, k=random.randint(2, 4)))

# 샘플 데이터 생성
def create_sample_breach_data(num_samples=300):
    data = []
    for _ in range(num_samples):
        name = fake.name()
        email = fake.email()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d")
        gender = random.choice(["M", "F"])
        ip = fake.ipv4()
        phone = fake.phone_number()
        address = fake.address().split('\n')[0]
        password_pattern = generate_password_patterns()

        data.append([
            email, name, birthday, gender,
            ip, phone, address, password_pattern
        ])

    df = pd.DataFrame(data, columns=[
        "email", "name", "birthday", "gender",
        "ip", "phone", "address", "password_pattern"
    ])
    return df

# CSV로 저장하기 (선택)
df = create_sample_breach_data(300)
df.to_csv("breach_sample_data.csv", index=False, encoding='utf-8-sig')

# 결과 확인
print(df.head())
