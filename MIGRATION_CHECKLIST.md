# PolyPilot — чеклист переезда на новый ПК

> Полная инструкция: `PolyPilot-Штаб/00_Старт/ПЕРЕХОД_НА_НОВЫЙ_ПК.md`

## На старом ПК

- [ ] `git add` + `commit` + `push` (весь штаб и код)
- [ ] `scripts\migration\backup-before-move.ps1` → флешка / облако
- [ ] Проверить в бэкапе: `backend.env`, `backend.runtime`
- [ ] Пароли: GitHub, Polza, Telegram, Vercel, Railway — в менеджере паролей

## На новом ПК

- [ ] Установить: Git, Cursor, Obsidian (+ Python 3.12 или копия `.runtime`)
- [ ] `git clone https://github.com/AndreySavinWB/polypilot-platform.git` → `d:\Andrey\PolyPilot`
- [ ] Восстановить `backend\.env` из бэкапа
- [ ] Восстановить `backend\.runtime` или установить Python
- [ ] `scripts\migration\setup-new-pc.ps1`
- [ ] Obsidian vault → `PolyPilot-Штаб`
- [ ] Cursor → открыть `d:\Andrey\PolyPilot`, прочитать `POLYPILOT_STATE.md`
- [ ] `backend\run.ps1` → `/health` OK
- [ ] Браузер: https://polypilot-platform.vercel.app/app/events.html

## После переезда (продолжение работы)

- [ ] Новый Agent-чат: «прочитай POLYPILOT_STATE.md, продолжаем этап 4c»
- [ ] Этап 4c: pipeline → OPEN CARD v2 (`sync_live_to_mvp.py`)
- [ ] Track A: Funnel 1.0 Pack #1

**Checkpoint:** `c498722` · feed «Что смотреть сейчас» · OPEN CARD v2 baseline `bc48e47`
