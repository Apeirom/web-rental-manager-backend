import os
from supabase import create_client, Client
from src.constants import SUPABASE_URL, SUPABASE_KEY


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("As variáveis SUPABASE_URL e SUPABASE_KEY não foram encontradas no .env!")

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseStorage:
    # Tiramos o valor padrão para forçar o Controller a dizer qual bucket quer usar
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = supabase_client

    def upload_file(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        self.client.storage.from_(self.bucket_name).upload(
            file=file_bytes,
            path=file_name,
            file_options={"content-type": content_type}
        )
        return self.get_public_url(file_name)

    def get_public_url(self, file_name: str) -> str:
        return self.client.storage.from_(self.bucket_name).get_public_url(file_name)

    def delete_file(self, file_name: str) -> None:
        self.client.storage.from_(self.bucket_name).remove([file_name])