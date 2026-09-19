# Turnos e ausência por professor e turno verification
**Verdict**: PASS
**Profile**: light
**Diff range**: 1b9e234..b5feae4
**Round**: 1 - full
**Verifier**: independent sub-agent (author != verifier)

## Binding sources

Profile light: o passo 1 (comparar checks contra fontes binding) não corre. O plano não marca fonte binding de contrato ou tela; Surface é None. Nenhuma tabela de Contradiction/Uncovered foi produzida.

## Checks

| Check | Claim | Proof run | Evidence | Result |
| --- | --- | --- | --- | --- |
| C1 | Cada turma possui exatamente um turno entre `MANHA`, `TARDE` e `NOITE` | `pytest tests -v` HEAD b5feae4 · `tests/cenarios/test_turno_e_etapa.py::test_turma_possui_exatamente_um_turno_valido` PASSED | `tests/cenarios/test_turno_e_etapa.py:42` `assert turnos == TURNOS_VALIDOS`; `tests/cenarios/test_turno_e_etapa.py:44` `assert grade_base.perfil_da_turma(id_turma).turno in TURNOS_VALIDOS` | PASS |
| C2 | Cada turma possui exatamente uma etapa entre `FUNDAMENTAL` e `MEDIO` | `pytest tests -v` · `tests/cenarios/test_turno_e_etapa.py::test_turma_possui_exatamente_uma_etapa_valida` PASSED | `tests/cenarios/test_turno_e_etapa.py:64` `assert grade_base.perfil_da_turma("TURMA_FUND").etapa == FUNDAMENTAL`; `tests/cenarios/test_turno_e_etapa.py:65` `assert grade_base.perfil_da_turma("TURMA_MEDIO").etapa == MEDIO` | PASS |
| C3 | Turma `FUNDAMENTAL` aceita no máximo 5 períodos e turma `MEDIO` aceita no máximo 6, dentro do próprio turno | `pytest tests -v` · `tests/cenarios/test_turno_e_etapa.py::test_teto_de_periodos_segue_a_etapa_da_turma` PASSED | `tests/cenarios/test_turno_e_etapa.py:90` `assert grade_base.perfil_da_turma("TURMA_FUND").teto_de_periodos == 5`; `tests/cenarios/test_turno_e_etapa.py:91` `assert grade_base.perfil_da_turma("TURMA_MEDIO").teto_de_periodos == 6` | PASS |
| C4 | Período acima do teto da etapa, ou turno da aula diferente do turno da turma, é rejeitado com `ERRO_VALIDACAO` antes do CP-SAT | `pytest tests -v` · `tests/cenarios/test_turno_e_etapa.py::test_periodo_ou_turno_incompativel_e_rejeitado_antes_do_solver` PASSED | `tests/cenarios/test_turno_e_etapa.py:121` `assert resultado.status == ERRO_VALIDACAO`; `tests/cenarios/test_turno_e_etapa.py:122` `assert construcoes == []` — o `for` em `:119` percorre período 6 no fundamental e turno distinto da turma | PASS |
| C5 | Ausência de um professor em um turno impede que ele permaneça alocado em qualquer aula daquele turno nos dias cobertos | `pytest tests -v` · `tests/cenarios/test_ausencia_por_turno.py::test_ausencia_impede_alocacao_do_professor_no_turno` PASSED | `tests/cenarios/test_ausencia_por_turno.py:46` `assert atribuicao.id_professor != professor_ausente` (quando `turno == MANHA` e `atribuicao.dia in dias`) | PASS |
| C6 | Sem restrição extra, a janela de alteração é o turno da ausência; aulas de outros turnos preservam professor, disciplina, turma, dia e período | `pytest tests -v` · `tests/cenarios/test_ausencia_por_turno.py::test_aulas_de_outros_turnos_sao_preservadas` PASSED | `tests/cenarios/test_ausencia_por_turno.py:83` `assert preservada.id_professor == aula_tarde.id_professor`; `:84` disciplina; `:85` turma; `:86` dia; `:87` `assert preservada.periodo == aula_tarde.periodo` | PASS |
| C7 | Professor ou turno da ausência inexistente na grade base retorna `ERRO_VALIDACAO` antes do solver | `pytest tests -v` · `tests/cenarios/test_ausencia_por_turno.py::test_professor_ou_turno_inexistente_e_rejeitado_antes_do_solver` PASSED | `tests/cenarios/test_ausencia_por_turno.py:100` `assert resultado.status == ERRO_VALIDACAO`; `tests/cenarios/test_ausencia_por_turno.py:101` `assert construcoes == []` — o `for` em `:98` percorre professor inexistente e turno `NOITE` ausente da grade | PASS |
| C8 | Professor sem aula no turno declarado, nos dias cobertos, retorna `CENARIO_VIAVEL` com a grade inalterada e zero alterações | `pytest tests -v` · `tests/cenarios/test_ausencia_por_turno.py::test_ausencia_sem_aula_no_turno_devolve_grade_inalterada` PASSED | `tests/cenarios/test_ausencia_por_turno.py:129` `assert resultado.status == CENARIO_VIAVEL`; `tests/cenarios/test_ausencia_por_turno.py:132` `assert solucao.atribuicoes == grade_base.aulas`; `tests/cenarios/test_ausencia_por_turno.py:133` `assert solucao.quantidade_de_alteracoes == 0` | PASS |

Amostragem e nível: C1 cobre os 3 turnos no mesmo conjunto; C2 afirma as 2 etapas; C3 afirma os 2 tetos; C4 e C7 cobrem os 2 membros de cada claim no mesmo laço, ambos abaixo da fronteira do solver (`construcoes == []`). Nenhum claim de N casos ficou provado só em subconjunto. Os oito nodeids existem no tree, entram no diff `1b9e234..b5feae4` e rodaram PASSED no HEAD `b5feae4`.

## Swept existing

Linhas `Swept` que apontam para código existente foram relidas no HEAD. As `n/a` aprovadas não foram investigadas.

- validation (C1, C2, C3, C4, C7): `src/gradeia/modules/cenarios/modelo.py:10`–`:12` declara `TURNOS_VALIDOS`, `ETAPAS_VALIDAS` e `PERIODOS_POR_ETAPA` (5/6); `Turma` em `:26`–`:33` carrega um `turno`, uma `etapa` e `teto_de_periodos`. `src/gradeia/modules/cenarios/validacao.py:23`–`:28` recusa turma inválida, período acima do teto e turno da aula diferente do da turma; `:32`–`:38` recusa professor inexistente e turno ausente da grade. `src/gradeia/modules/scheduling/or_tools_scheduling_engine.py:50`–`:53` devolve `ERRO_VALIDACAO` antes de `_resolver`.
- failure modes (C4, C7): as duas rejeições saem em `:50`–`:53` com `ERRO_VALIDACAO` e sem construir o modelo CP-SAT.
- idempotency / authorization / concurrency / data lifecycle / dependency failure: n/a — política aprovada; nada no código para estar errado.
- state transitions (C4, C7, C8): `src/gradeia/modules/cenarios/resultado.py:5`–`:7` declara `CENARIO_VIAVEL`, `CENARIO_INVIAVEL` e `ERRO_VALIDACAO`; o motor emite `ERRO_VALIDACAO` em `:51` e `:53`, e `CENARIO_VIAVEL` com a grade base em `:54`–`:60` quando não há aula afetada.
- observability (C6, C8): `or_tools_scheduling_engine.py:81`–`:85` só move aula cujo turno é o da ausência e está na janela; as demais ficam em `aulas_fixas`. Sem aula afetada, `:57`–`:59` devolve `SolucaoDeCenario(atribuicoes=grade_base.aulas)`.

## Gate

`cd /home/vicente/Documentos/grade-escolar/gradeIA && .venv/bin/pytest tests -v` — 22 passed, 0 failed.

A invocação pedida coletou 22 itens. `pyproject.toml` define `addopts = "-q"`, então `-v` e `-q` se cancelam e o runner imprimiu pontos por arquivo. Relançado com `.venv/bin/pytest tests -o addopts= -v`: os oito nodeids de C1–C8 aparecem individualmente como PASSED no HEAD `b5feae4bf7e91d75f6e076e1f6ad276cfd16e3af`.
