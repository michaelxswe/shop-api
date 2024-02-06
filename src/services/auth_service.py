import time
import uuid

import jwt
import redis
from models import AccessTokenModel


class AuthService:
    def invoke_access_token(self, tid: str, redis: redis.Redis) -> None:
        redis.set(f"invalid_access_token:{tid}", "1", 3600)

    def set_access_token_min_issue_date(self, user_id: int, redis: redis.Redis) -> None:
        curr_unix_time = int(time.time())
        redis.set(f"user:{user_id}:access_token_min_issue_date", curr_unix_time, 3600)

    def create_access_token(self, user_id: int, key: str, algorithm: str) -> AccessTokenModel:
        tid = str(uuid.uuid4())
        issue_date = int(time.time())
        exp = issue_date + 1800  # 30 mins
        payload = {"sub": user_id, "exp": exp, "issue_date": issue_date, "tid": tid}
        access_token = jwt.encode(payload=payload, key=key, algorithm=algorithm)
        return AccessTokenModel(type="bearer", value=access_token)

    def validate_access_token(self, access_token: str, key: str, algorithm: str, redis: redis.Redis) -> dict | None:
        claims = jwt.decode(
            jwt=access_token,
            key=key,
            algorithms=[algorithm],
        )

        user_id, tid, issue_date = claims["sub"], claims["tid"], claims["issue_date"]

        pipeline = redis.pipeline()
        pipeline.get(f"invalid_access_token:{tid}")
        pipeline.get(f"user:{user_id}:access_token_min_issue_date")
        res = pipeline.execute()
        invalid_access_token, access_token_min_issue_date = res[0], res[1]

        if invalid_access_token:
            return None

        if access_token_min_issue_date and issue_date < int(access_token_min_issue_date):
            return None

        return claims
