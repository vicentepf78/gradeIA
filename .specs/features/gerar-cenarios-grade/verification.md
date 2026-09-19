# Gerar cenários de reorganização da grade verification

**Verdict**: PASS
**Profile**: light
**Diff range**: 4d41ce8..a42f9d9
**Round**: 1 - full
**Verifier**: independent sub-agent (author != verifier)

## Binding sources

Profile light: o passo 1 (comparar checks contra fontes binding) não corre. O documento citado pelo plano foi aberto nas seções de POC, Scheduling Engine e restrições obrigatórias somente como contexto; nenhuma tabela de Contradiction/Uncovered foi produzida.

## Checks

| Check | Claim | Proof run | Evidence | Result |
| --- | --- | --- | --- | --- |
| C1 | Cada `AtribuicaoDeAula` aceita exatamente um professor, disciplina, turma, dia e período existentes na `GradeBase` | `pytest tests -v` HEAD a42f9d9 · `tests/cenarios/test_validacao_cenario.py::test_atribuicao_com_referencias_existentes_e_aceita` na suíte de 13 passed | `tests/cenarios/test_validacao_cenario.py:12` `aula.id_professor in grade_base.professores` (e os quatro `in` irmãos em `:13`–`:16`); `tests/cenarios/test_validacao_cenario.py:29` `resultado.status != ERRO_VALIDACAO` | PASS |
| C2 | Uma ausência declarada impede o professor ausente de permanecer alocado dentro da janela do cenário | `pytest tests -v` · `tests/cenarios/test_ausencia_professor.py::test_ausencia_impede_alocacao_do_professor_na_janela` | `tests/cenarios/test_ausencia_professor.py:31` `assert atribuicao.id_professor != professor_ausente` (quando `(dia, periodo)` está em `cenario.ausencia.dias_periodos`) | PASS |
| C3 | Referência inexistente a professor, turma, disciplina, dia ou período é rejeitada antes do CP-SAT | `pytest tests -v` · `tests/cenarios/test_validacao_cenario.py::test_referencias_inexistentes_sao_rejeitadas_antes_do_solver` | `tests/cenarios/test_validacao_cenario.py:48` `resultado.status == ERRO_VALIDACAO`; `tests/cenarios/test_validacao_cenario.py:49` `construcoes == []` — o `for` em `:44` percorre os 5 campos da claim | PASS |
| C4 | Janela que não cobre todas as aulas afetadas retorna `CENARIO_INVIAVEL` e identifica as aulas fora da janela | `pytest tests -v` · `tests/cenarios/test_janela_de_alteracao.py::test_janela_insuficiente_retorna_cenario_inviavel_com_aulas_afetadas` | `tests/cenarios/test_janela_de_alteracao.py:31` `resultado.status == CENARIO_INVIAVEL`; `tests/cenarios/test_janela_de_alteracao.py:35` `resultado.aulas_fora_da_janela == (aula_fora_da_janela,)` | PASS |
| C5 | Toda solução viável tem no máximo uma aula por professor/dia/período e por turma/dia/período | `pytest tests -v` · `tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_nao_cria_conflito_de_professor_nem_de_turma` | `tests/scheduling/test_restricoes_obrigatorias.py:49` `chave_professor not in ocupacao_professor`; `tests/scheduling/test_restricoes_obrigatorias.py:50` `chave_turma not in ocupacao_turma` | PASS |
| C6 | Toda aula de solução viável vai só a professor habilitado e disponível no dia/período | `pytest tests -v` · `tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_respeita_habilitacao_e_disponibilidade_do_professor` | `tests/scheduling/test_restricoes_obrigatorias.py:99` `atribuicao.id_disciplina in perfil.disciplinas_habilitadas`; `tests/scheduling/test_restricoes_obrigatorias.py:100` `(atribuicao.dia, atribuicao.periodo) in perfil.disponibilidade` | PASS |
| C7 | Toda solução viável preserva a quantidade de aulas de cada combinação turma/disciplina da grade base | `pytest tests -v` · `tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_preserva_quantidade_de_aulas_por_turma_e_disciplina` | `tests/scheduling/test_restricoes_obrigatorias.py:151` `carga_da_solucao == carga_da_base` | PASS |
| C8 | Aula fora da janela preserva professor, disciplina, turma, dia e período da grade base | `pytest tests -v` · `tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_preserva_atribuicoes_fora_da_janela_de_alteracao` | `tests/scheduling/test_restricoes_obrigatorias.py:186` `preservada.id_professor == aula_fora_da_janela.id_professor` (e os quatro irmãos em `:187`–`:190` para disciplina, turma, dia, período) | PASS |
| C9 | Sem alternativa que satisfaça as restrições retorna `CENARIO_INVIAVEL` sem solução parcial viável | `pytest tests -v` · `tests/scheduling/test_cenario_inviavel.py::test_solver_sem_alternativa_retorna_cenario_inviavel_sem_solucao_parcial` | `tests/scheduling/test_cenario_inviavel.py:35` `resultado.status == CENARIO_INVIAVEL`; `tests/scheduling/test_cenario_inviavel.py:36` `resultado.solucoes == ()` | PASS |
| C10 | Simulação viável retorna de uma a cinco soluções estruturalmente distintas | `pytest tests -v` · `tests/cenarios/test_comparacao_de_solucoes.py::test_resultado_limita_a_cinco_solucoes_distintas` | `tests/cenarios/test_comparacao_de_solucoes.py:113` `1 <= len(resultado.solucoes) <= 5`; `tests/cenarios/test_comparacao_de_solucoes.py:114` `len(resultado.solucoes) == 5`; `tests/cenarios/test_comparacao_de_solucoes.py:116` `len(set(estruturas)) == len(estruturas)` | PASS |
| C11 | Cada solução informa alterações, professores afetados, aulas deslocadas e janelas criadas contra a grade base | `pytest tests -v` · `tests/cenarios/test_comparacao_de_solucoes.py::test_solucao_expoe_todas_as_metricas_de_impacto` | `tests/cenarios/test_comparacao_de_solucoes.py:145` `solucao.quantidade_de_alteracoes == 1`; `:146` `professores_afetados == frozenset({"PROFESSOR_001", "PROFESSOR_002"})`; `:149` `quantidade_de_aulas_deslocadas == 0`; `:150` `janelas_criadas == 1` | PASS |
| C12 | Soluções retornadas são ordenadas por alterações, professores afetados, aulas deslocadas e janelas criadas, nesta precedência | `pytest tests -v` · `tests/cenarios/test_comparacao_de_solucoes.py::test_solucoes_sao_ordenadas_por_tupla_lexicografica_de_impacto` | `tests/cenarios/test_comparacao_de_solucoes.py:261` chaves `[(1, 2, 0, 0), (1, 2, 0, 1), (1, 2, 1, 0), (2, 1, 2, 0)]`; `tests/cenarios/test_comparacao_de_solucoes.py:274` `resultado.solucoes == tuple(sorted(resultado.solucoes, key=chave_lexicografica))` | PASS |
| C13 | Mesma grade base e mesmo cenário produzem as mesmas soluções na mesma ordem | `pytest tests -v` · `tests/cenarios/test_comparacao_de_solucoes.py::test_mesma_entrada_produz_mesmas_solucoes_na_mesma_ordem` | `tests/cenarios/test_comparacao_de_solucoes.py:288` `resultado1.solucoes == resultado2.solucoes` | PASS |

Amostragem e nível: C3 cobre os 5 membros da claim no mesmo laço; C8 afirma os 5 campos protegidos; C11 afirma as 4 métricas com os valores da prova atual (1, {PROFESSOR_001, PROFESSOR_002}, 0, 1); C12 afirma a precedência das 4 chaves e a ordem no resultado de `simular`. Nenhum claim de N casos ficou provado só em subconjunto.

## Swept existing

Linhas `Swept` que apontam para código existente foram relidas no HEAD. As `n/a` aprovadas não foram investigadas.

- validation (C1, C3, C4): `src/gradeia/modules/cenarios/validacao.py:9` `referencias_da_grade_sao_validas` recusa professor/disciplina/turma/dia/período ausentes; `src/gradeia/modules/scheduling/or_tools_scheduling_engine.py:46` devolve `ERRO_VALIDACAO` antes do solver; `:49`–`:54` devolve `CENARIO_INVIAVEL` com `aulas_fora_da_janela` quando a janela não cobre as aulas afetadas.
- failure modes (C4, C9): além da janela insuficiente, `or_tools_scheduling_engine.py:107` e `:182` devolvem `CENARIO_INVIAVEL` sem popular `solucoes` (default `()`).
- idempotency (C13): `or_tools_scheduling_engine.py:176` `random_seed = SEMENTE_ALEATORIA`; `:177` `num_search_workers = 1`; o comparador ordena por chave determinística.
- state transitions (C4, C9, C10): `src/gradeia/modules/cenarios/resultado.py:5`–`:7` declara `CENARIO_VIAVEL`, `CENARIO_INVIAVEL` e `ERRO_VALIDACAO`; o motor emite os três.
- observability (C11): `src/gradeia/modules/cenarios/comparador.py:54`–`:59` preenche `quantidade_de_alteracoes`, `professores_afetados`, `quantidade_de_aulas_deslocadas` e `janelas_criadas`.

## Gate

`cd /home/vicente/Documentos/grade-escolar/gradeIA && .venv/bin/pytest tests -v` — 13 passed, 0 failed.

A invocação coletou 13 itens. `pyproject.toml` define `addopts = "-q"`, então `-v` e `-q` se cancelam e o runner imprimiu pontos por arquivo, não o nodeid `PASSED`. Os 13 `def test_` em `tests/` são exatamente os 13 nodeids nomeados em `checks.md`; collected 13 / passed 13 no HEAD `a42f9d97c93f642c733d8211c3afaed493e35f8c`.
