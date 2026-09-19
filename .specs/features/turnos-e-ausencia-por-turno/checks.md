# Turnos e ausência por professor e turno checks

Profile: light
Plan: `.specs/features/turnos-e-ausencia-por-turno/plan.md`

8 checks in 2 slices · 3 one-way doors · 0 open, of which 0 block

## Checks

### S1 - modelar turno, etapa e carga de períodos · 5 arquivos · 28 KB · ~7k

**C1** ✓ (feito) - Cada turma possui exatamente um turno entre `MANHA`, `TARDE` e `NOITE` (AC 1).
Proof: `pytest tests/cenarios/test_turno_e_etapa.py::test_turma_possui_exatamente_um_turno_valido`

**C2** ✓ (feito) - Cada turma possui exatamente uma etapa entre `FUNDAMENTAL` e `MEDIO` (AC 2).
Proof: `pytest tests/cenarios/test_turno_e_etapa.py::test_turma_possui_exatamente_uma_etapa_valida`

**C3** ✓ (feito) - Turma `FUNDAMENTAL` aceita no máximo 5 períodos e turma `MEDIO` aceita no máximo 6, dentro do próprio turno (AC 3).
Proof: `pytest tests/cenarios/test_turno_e_etapa.py::test_teto_de_periodos_segue_a_etapa_da_turma`

**C4** ✓ (feito) - Período acima do teto da etapa, ou turno da aula diferente do turno da turma, é rejeitado com `ERRO_VALIDACAO` antes do CP-SAT (AC 4).
Proof: `pytest tests/cenarios/test_turno_e_etapa.py::test_periodo_ou_turno_incompativel_e_rejeitado_antes_do_solver`

### S2 - declarar falta pelo professor e pelo turno · 6 arquivos · 32 KB · ~8k

**C5** ✓ (feito) - Ausência de um professor em um turno impede que ele permaneça alocado em qualquer aula daquele turno nos dias cobertos (AC 5).
Proof: `pytest tests/cenarios/test_ausencia_por_turno.py::test_ausencia_impede_alocacao_do_professor_no_turno`

**C6** ✓ (feito) - Sem restrição extra, a janela de alteração é o turno da ausência; aulas de outros turnos preservam professor, disciplina, turma, dia e período (AC 6).
Proof: `pytest tests/cenarios/test_ausencia_por_turno.py::test_aulas_de_outros_turnos_sao_preservadas`

**C7** ✓ (feito) - Professor ou turno da ausência inexistente na grade base retorna `ERRO_VALIDACAO` antes do solver (AC 7).
Proof: `pytest tests/cenarios/test_ausencia_por_turno.py::test_professor_ou_turno_inexistente_e_rejeitado_antes_do_solver`

**C8** ✓ (feito) - Professor sem aula no turno declarado, nos dias cobertos, retorna `CENARIO_VIAVEL` com a grade inalterada e zero alterações (AC 8).
Proof: `pytest tests/cenarios/test_ausencia_por_turno.py::test_ausencia_sem_aula_no_turno_devolve_grade_inalterada`

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| turnos (3) | `MANHA` C1 · `TARDE` C1 · `NOITE` C1 | - |
| etapas (2) | `FUNDAMENTAL` C2 · `MEDIO` C2 | - |
| teto de períodos (2) | 5 no `FUNDAMENTAL` C3 · 6 no `MEDIO` C3 | - |
| rejeições de aula (2) | período acima do teto C4 · turno diferente da turma C4 | - |
| ausência inválida (2) | professor inexistente C7 · turno inexistente C7 | - |
| entidades (8) | `Turma` C1 · `Turno` C1 · `EtapaDeEnsino` C2 · `AtribuicaoDeAula` C4 · `AusenciaDeProfessor` C5 · `Cenario` C5 · `Professor` C5 · `GradeBase` C8 | - |
| portas de arquitetura (3) | período relativo ao turno e à etapa C3 · ausência por professor e turno C5 · janela padrão igual ao turno C6 | - |
| resultados do cenário (2) | `ERRO_VALIDACAO` C4 · `CENARIO_VIAVEL` inalterado C8 | - |

- Nenhuma rota HTTP foi definida no plano; portanto, não há status HTTP a cobrir.
- Nenhum check afirma mais do que o caso exercitado pela sua prova.

## Swept

- validation: C1, C2, C3, C4, C7
- failure modes: C4, C7
- idempotency: n/a - esta fatia não exige duas execuções iguais; o determinismo da simulação já foi fechado na feature anterior.
- authorization: n/a - o POC não expõe usuário, credencial ou endpoint.
- concurrency: n/a - cada simulação continua isolada.
- data lifecycle: n/a - o POC não persiste dados.
- dependency failure: n/a - OR-Tools segue no mesmo processo.
- state transitions: C4, C7, C8
- observability: C6, C8

## Handoff

- S1 = 28 KB; S2 acrescenta 32 KB; dataset e fábricas acrescentam aproximadamente 16 KB. Estimativa total: 76 KB / 4 = aproximadamente 19k tokens, abaixo do orçamento `light` de 150k - one builder.
- **Boundary:** C1-C8 closed, aguardando commit
- **Settled mid-build:** none
- **Abandoned:** none
