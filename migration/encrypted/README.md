# Encrypted migration bundle

Секреты и portable Python **не лежат в git открытым текстом** — только зашифрованный файл.

| Файл | Назначение |
|------|------------|
| `polypilot-migration.enc` | AES-256 bundle (.env, .runtime, Cursor) |
| `polypilot-migration.meta.json` | salt/iv (без пароля) |

## Новый ПК (2 команды)

```powershell
git clone https://github.com/AndreySavinWB/polypilot-platform.git d:\Andrey\PolyPilot
cd d:\Andrey\PolyPilot
$env:PP_MIGRATION_PASSWORD = "ВАШ_ПАРОЛЬ"
powershell -ExecutionPolicy Bypass -File scripts\migration\restore-from-github.ps1
cd backend
.\run.ps1
```

Пароль храни в менеджере паролей — **не в репозитории**.

## Обновить bundle (старый ПК)

```powershell
$env:PP_MIGRATION_PASSWORD = "ВАШ_ПАРОЛЬ"
powershell -ExecutionPolicy Bypass -File scripts\migration\create-encrypted-bundle.ps1
git add migration/encrypted/
git commit -m "Update encrypted migration bundle."
git push
```
