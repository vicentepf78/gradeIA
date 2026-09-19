# Project state

## Decisions

| ID | Decision | Rationale | Status | Date |
| --- | --- | --- | --- | --- |
| AD-001 | POC Python isolado em `gradeIA/` na branch `poc-grade-semanal` | o repositório remoto estava vazio; o desenvolvimento da feature não mistura os documentos de pesquisa do diretório pai | active | 2026-09-19 |
| AD-002 | Período é ordinal dentro do turno da turma; teto 5 no `FUNDAMENTAL` e 6 no `MEDIO`; turnos `MANHA`, `TARDE` e `NOITE` | o pedido pedagógico é por turno e etapa, não por uma grade plana de 6 períodos | active | 2026-09-19 |

## Handoff

**Feature**: turnos-e-ausencia-por-turno
**Where**: verification PASS - C1–C8 verdes; `validate_verification.py` exit 0
**In progress**: none
**Next step**: nenhum — feature fechada no profile light
**Blockers**: none
**Uncommitted**: `verification.md`
**Branch**: poc-grade-semanal
