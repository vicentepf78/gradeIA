# Gerar cenários de reorganização da grade checks

Profile: light
Plan: `.specs/features/gerar-cenarios-grade/plan.md`

13 checks in 3 slices · 3 one-way doors · 0 open, of which 0 block

## Checks

### S1 - modelar uma grade semanal e um cenário de ausência · 6 arquivos · 24 KB · ~6k

**C1** ✓ (feito) - Cada `AtribuicaoDeAula` aceita exatamente um professor, disciplina, turma, dia e período existentes na `GradeBase` (AC 1).
Proof: `pytest tests/cenarios/test_validacao_cenario.py::test_atribuicao_com_referencias_existentes_e_aceita`

**C2** - Uma ausência declarada impede o professor ausente de permanecer alocado dentro da janela do cenário (AC 2).
Proof: `pytest tests/cenarios/test_ausencia_professor.py::test_ausencia_impede_alocacao_do_professor_na_janela`

**C3** ✓ (feito) - Uma atribuição que referencia professor, turma, disciplina, dia ou período inexistente é rejeitada antes da criação do modelo CP-SAT (AC 3).
Proof: `pytest tests/cenarios/test_validacao_cenario.py::test_referencias_inexistentes_sao_rejeitadas_antes_do_solver`

**C4** ✓ (feito) - Um cenário cuja janela não permite alterar todas as aulas afetadas retorna `CENARIO_INVIAVEL` e identifica as aulas fora da janela (AC 4).
Proof: `pytest tests/cenarios/test_janela_de_alteracao.py::test_janela_insuficiente_retorna_cenario_inviavel_com_aulas_afetadas`

### S2 - gerar alternativas viáveis com CP-SAT · 8 arquivos · 48 KB · ~12k

**C5** - Toda solução viável contém no máximo uma aula por combinação de professor/dia/período e por combinação de turma/dia/período (AC 5).
Proof: `pytest tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_nao_cria_conflito_de_professor_nem_de_turma`

**C6** - Toda aula de uma solução viável é atribuída somente a professor habilitado para a disciplina e disponível no dia e período da aula (AC 6).
Proof: `pytest tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_respeita_habilitacao_e_disponibilidade_do_professor`

**C7** - Toda solução viável preserva a quantidade total de aulas de cada combinação turma/disciplina da grade base (AC 7).
Proof: `pytest tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_preserva_quantidade_de_aulas_por_turma_e_disciplina`

**C8** - Toda aula fora da janela de alteração preserva professor, disciplina, turma, dia e período da grade base (AC 8).
Proof: `pytest tests/scheduling/test_restricoes_obrigatorias.py::test_solucao_preserva_atribuicoes_fora_da_janela_de_alteracao`

**C9** - Uma simulação sem alternativa que satisfaça as restrições retorna `CENARIO_INVIAVEL` sem apresentar solução parcial como viável (AC 9).
Proof: `pytest tests/scheduling/test_cenario_inviavel.py::test_solver_sem_alternativa_retorna_cenario_inviavel_sem_solucao_parcial`

### S3 - comparar e explicar opções de reorganização · 5 arquivos · 24 KB · ~6k

**C10** - Uma simulação viável retorna de uma a cinco soluções estruturalmente distintas (AC 10).
Proof: `pytest tests/cenarios/test_comparacao_de_solucoes.py::test_resultado_limita_a_cinco_solucoes_distintas`

**C11** - Cada solução informa quantidade de alterações, professores afetados, aulas deslocadas e janelas criadas contra a grade base (AC 11).
Proof: `pytest tests/cenarios/test_comparacao_de_solucoes.py::test_solucao_expoe_todas_as_metricas_de_impacto`

**C12** - Soluções retornadas são ordenadas por quantidade de alterações, professores afetados, aulas deslocadas e janelas criadas, nesta precedência (AC 12).
Proof: `pytest tests/cenarios/test_comparacao_de_solucoes.py::test_solucoes_sao_ordenadas_por_tupla_lexicografica_de_impacto`

**C13** - Duas execuções com a mesma grade base e o mesmo cenário retornam as mesmas soluções na mesma ordem (AC 13).
Proof: `pytest tests/cenarios/test_comparacao_de_solucoes.py::test_mesma_entrada_produz_mesmas_solucoes_na_mesma_ordem`

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| entidades e relações (8) | `GradeBase` C1 · `Cenario` C2 · `RestricaoDeCenario` C4 · `SolucaoDeCenario` C10 · `AtribuicaoDeAula` C1 · `Professor` C6 · `Disciplina` C6 · `Turma` C5 | - |
| atributos obrigatórios da atribuição (5) | `professor` C1 · `disciplina` C1 · `turma` C1 · `dia` C1 · `periodo` C1 | - |
| referências inválidas (5) | `professor` C3 · `turma` C3 · `disciplina` C3 · `dia` C3 · `periodo` C3 | - |
| restrições obrigatórias do solver (4) | conflito de professor C5 · conflito de turma C5 · habilitação/disponibilidade C6 · quantidade por turma/disciplina C7 | - |
| atribuições protegidas pelo cenário (5) | `professor` C8 · `disciplina` C8 · `turma` C8 · `dia` C8 · `periodo` C8 | - |
| resultados inviáveis (2) | janela insuficiente C4 · nenhuma alternativa viável C9 | - |
| soluções retornadas (5) | limite de cinco C10 · distinção estrutural C10 · alterações C11 · professores afetados C11 · aulas deslocadas/janelas criadas C11 | - |
| ordenação de impacto (4) | alterações C12 · professores afetados C12 · aulas deslocadas C12 · janelas criadas C12 | - |
| portas de arquitetura (3) | `SchedulingEngine`/`OrToolsSchedulingEngine` C5-C9 · `Cenario` sobre `GradeBase` imutável C8 · tupla lexicográfica C12 | - |

- Nenhuma rota externa foi definida no plano; portanto, não há status HTTP a cobrir.
- Nenhum check afirma mais do que o caso exercitado pela sua prova.

## Swept

- validation: C1, C3, C4
- failure modes: C4, C9
- idempotency: C13
- authorization: n/a - o POC não expõe usuário, credencial ou endpoint.
- concurrency: n/a - cada simulação é uma execução isolada e o POC não persiste nem compartilha uma grade mutável.
- data lifecycle: n/a - o POC não persiste dados.
- dependency failure: n/a - OR-Tools executa no mesmo processo; falhas de disponibilidade externa não fazem parte deste POC.
- state transitions: C4, C9, C10
- observability: C11

## Handoff

- S1 = 24 KB; S2 acrescenta 48 KB; S3 acrescenta 24 KB; configuração e fixtures acrescentam aproximadamente 12 KB. Estimativa total: 108 KB / 4 = aproximadamente 27k tokens, abaixo do orçamento `light` de 150k - one builder.
- S1 C1/C3/C4 fechados nesta fatia. C2 não fecha aqui: `Cenario` e `AusenciaDeProfessor` estão modelados; a prova `test_ausencia_impede_alocacao_do_professor_na_janela` fica para S2 com o motor CP-SAT.
