from django.db.models import Q
from rest_framework_jwt.settings import api_settings
from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField, CharField
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'transcript',
            'id_number',
            'birth_date',
            'career'
        ]


class UserCreateSerializer(ModelSerializer):
    email = EmailField(label='Email address')
    validation_email = EmailField(label='Confirm Email', write_only=True)
    password = CharField(write_only=True, style={'input_type': 'password'})
    validation_password = CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'validation_email',
            'transcript',
            'id_number',
            'birth_date',
            'career',
            'password',
            'validation_password'
        ]

    def validate_email(self, value):
        data = self.get_initial()
        email = value
        validation_email = data.get("validation_email")
        if email != validation_email:
            raise ValidationError("Emails must match")

        user_qs = User.objects.filter(email=email)

        if user_qs.exists():
            raise ValidationError("This user is already registered")
        return value

    def validate_validation_email(self, value):
        data = self.get_initial()
        email = data.get("email")
        validation_email = value

        if email != validation_email:
            raise ValidationError("Emails must match")

        return value

    def validate_password(self, value):
        data = self.get_initial()
        password = value
        validation_password = data.get("validation_password")

        if password != validation_password:
            raise ValidationError("Passwords must match")

        return value

    def validate_validation_password(self, value):
        data = self.get_initial()
        password = data.get("password")
        validation_password = value

        if password != validation_password:
            raise ValidationError("Passwords must match")

        return value

    def create(self, validated_data):
        user_obj = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            transcript=validated_data['transcript'],
            id_number=validated_data['id_number'],
            birth_date=validated_data['birth_date'],
            career=validated_data['career']
        )
        user_obj.set_password(validated_data['password'])
        user_obj.save()

        return validated_data


class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    username = CharField(allow_blank=True, required=False)
    email = EmailField(label='Email address', allow_blank=True, required=False)
    password = CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'token'
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        email = data.get('email', None)
        username = data.get('username', None)
        password = data['password']

        if not email and not username:
            raise ValidationError("A username or Email is required to login")

        user = User.objects.filter(
            Q(email=data.get('email', None))|
            Q(username=data.get('username', None))
        ).distinct()
        user = user.exclude(email__iexact='')

        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("This username/email is not valid.")

        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect credentials, please try again.")

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user_obj)
        token = jwt_encode_handler(payload)

        data['token'] = token

        return data
