import sqlite3
import os

DB='db.sqlite3'
if not os.path.exists(DB):
    print('NO_DB')
    raise SystemExit(1)

con=sqlite3.connect(DB)
cur=con.cursor()

tables=['auth_user','oficinatech01_funcionario','oficinatech01_fornecedor','oficinatech01_peca','oficinatech01_venda','oficinatech01_entrada','django_session','django_content_type','auth_permission','auth_group','django_migrations']
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        r=cur.fetchone()[0]
    except Exception as e:
        r=f'ERR ({e})'
    print(f"{t}: {r}")

# Also list user ids sample
try:
    cur.execute("SELECT id, username FROM auth_user LIMIT 10")
    rows=cur.fetchall()
    print('\nSample auth_user rows:')
    for row in rows:
        print(row)
except Exception:
    pass

con.close()
