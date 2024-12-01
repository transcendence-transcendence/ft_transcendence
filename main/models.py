from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import pyotp, base64

class UserManager(BaseUserManager):
    # def create_user(self, email, username=None, password=None, **extra_fields):
    #     if not email:
    #         raise ValueError('Users must have an email address')
    #     email = self.normalize_email(email)
    #     user = self.model(email=email, username=username, **extra_fields)
    #     user.set_password(password)  # 비밀번호 해시
    #     user.save(using=self._db)
    #     return user

    # def create_superuser(self, email, username=None, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)

    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')

    #     return self.create_user(email, username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})  # USERNAME_FIELD에 따라 사용자 검색

# 사용자 모델                       
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)  # 이메일 필드
    password = models.CharField(max_length=255)             # 암호화된 비밀번호
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)  # 사용자명
    is_active = models.BooleanField(default=True)           # 활성화 상태
    is_staff = models.BooleanField(default=False)           # 직원 권한 여부
    profile = models.TextField(null=True, blank=True)       # 프로필 정보
    otp_key = models.CharField(max_length=32, default=pyotp.random_base32)  # OTP 키
    is_otp_verified = models.BooleanField(default=False)  # 2FA 인증 여부

    objects = UserManager()  # 커스텀 매니저

    # 로그인 시 사용할 필드 설정
    USERNAME_FIELD = 'username'  # 기본적으로 `username` 필드를 사용하여 로그인

    # 사용자 생성 시 필수로 요구할 추가 필드 설정
    REQUIRED_FIELDS = ['email']  # 슈퍼유저 생성 시 `email`을 필수로 요구

    def __str__(self):
        return self.username or self.email


# 게임 (Game) 모델
class Game(models.Model):
    GAME_TYPE_CHOICES = [
        ('regular', 'Regular'),        # 일반 경기
        ('tournament', 'Tournament'),  # 토너먼트 경기
    ]

    player1 = models.ForeignKey(User, related_name="games_as_player1", on_delete=models.CASCADE)  # 첫 번째 플레이어
    score1 = models.IntegerField(null=True, blank=True)      # 첫 번째 플레이어 점수
    player2 = models.ForeignKey(User, related_name="games_as_player2", on_delete=models.CASCADE)  # 두 번째 플레이어
    score2 = models.IntegerField(null=True, blank=True)      # 두 번째 플레이어 점수
    winner = models.ForeignKey(User, related_name="wins", on_delete=models.CASCADE, null=True, blank=True)  # 승자
    date = models.DateField(null=True, blank=True)           # 게임 날짜
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default='regular')  # 게임 유형 (일반 경기 or 토너먼트)
    round = models.IntegerField(default=1)  # 라운드 번호 (토너먼트에서만 사용)

    def __str__(self):
        return f"Game on {self.date} - {self.player1.username} vs {self.player2.username}"

# 친구 (Relation) 모델
class Relation(models.Model):
    requester = models.ForeignKey(User, related_name="requested_relations", on_delete=models.CASCADE)  # 친구 요청자
    receiver = models.ForeignKey(User, related_name="received_relations", on_delete=models.CASCADE)    # 친구 수락자

    def __str__(self):
        return f"{self.requester.username} -> {self.receiver.username}"
