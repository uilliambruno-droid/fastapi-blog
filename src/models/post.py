import sqlalchemy as sa

from src.database import metadata

posts = sa.Table(
    "posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("title", sa.String(255), nullable=False),
    sa.Column("content", sa.Text, nullable=False),
    sa.Column("published", sa.Boolean, default=False),
    sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    sa.Column("date", sa.DateTime, default=sa.func.now()),
)
