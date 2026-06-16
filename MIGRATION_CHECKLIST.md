# PolyPilot — чеклист переезда на новый ПК

> Полная инструкция: `PolyPilot-Штаб/00_Старт/ПЕРЕХОД_НА_НОВЫЙ_ПК.md`

## На старом ПК

- [ ] `git add` + `commit` + `push` (весь штаб и код)
- [ ] `scripts\migration\backup-before-move.ps1` → флешка / облако
- [ ] Проверить в бэкапе: `backend.env`, `backend.runtime`
- [ ] Пароли: GitHub, Polza, Telegram, Vercel, Railway — в менеджере паролей

## На новом ПК (самый простой путь — через GitHub)

- [ ] `git clone https://github.com/AndreySavinWB/polypilot-platform.git` → `d:\Andrey\PolyPilot`
- [ ] Открыть пароль из менеджера паролей (файл `migration/encrypted/PASSWORD.local.txt` только на **старом** ПК)
- [ ] `$env:PP_MIGRATION_PASSWORD = "..."` → `scripts\migration\restore-from-github.ps1`
- [ ] `backend\run.ps1` → `/health` OK

## На старом ПК (если ещё не сделано)

- [ ] `git pull` + `git push` (весь код + `migration/encrypted/polypilot-migration.enc`)
- [ ] Сохранить пароль из `migration/encrypted/PASSWORD.local.txt` в менеджер паролей / Telegram «Избранное»

## После переезда (продолжение работы)

- [ ] Новый Agent-чат: «прочитай POLYPILOT_STATE.md, продолжаем этап 4c»
- [ ] Этап 4c: pipeline → OPEN CARD v2 (`sync_live_to_mvp.py`)
- [ ] Track A: Funnel 1.0 Pack #1

**Checkpoint:** `c498722` · feed «Что смотреть сейчас» · OPEN CARD v2 baseline `bc48e47`
