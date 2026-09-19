# gradeIA — POC de cenários da grade

Biblioteca Python que simula a ausência de um professor e devolve até
cinco reorganizações viáveis da grade semanal. Não há interface web,
API HTTP nem banco de dados neste POC: você instala o pacote e executa
o motor no terminal.

## O que você precisa

- Python 3.12 ou superior
- Trabalhar na pasta `gradeIA` (este repositório)

## Como instalar

No diretório `gradeIA`, crie o ambiente e instale o pacote em modo
editável:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Se você usa `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

A instalação traz o OR-Tools (solver CP-SAT) e o pytest.

## Já existe um dataset?

Sim. O arquivo `dados/grade-basica.json` é uma grade sintética pronta
para o motor:

- 4 professores: Ana (matemática), Bruno (português e matemática),
  Carla (história e português) e Diego (ciências e matemática)
- 3 turmas: 8A e 8B no fundamental de manhã (5 períodos); 9A no médio
  à tarde (6 períodos)
- turnos `MANHA`, `TARDE` e `NOITE`
- 27 aulas
- cenário embutido: Ana falta no turno `MANHA` na segunda; a tarde da
  9A não entra na janela

Os IDs no JSON usam camelCase (`idProfessor`, `idDisciplina`,
`idTurma`). O período é a ordem da aula **dentro do turno** da turma.

Os CSVs em `../dados-brutos/uff-2025-1/` não servem neste POC. São
turmas de graduação da UFF, sem o modelo mínimo de
professor + disciplina + turma + dia + período que o motor exige.

## Como “subir” e testar a aplicação

Não existe um servidor para levantar. O ponto de entrada é o módulo
da biblioteca. Com o ambiente ativado e o diretório atual em
`gradeIA`:

```bash
python -m gradeia
```

Isso carrega `dados/grade-basica.json`, roda
`SchedulingEngine.simular` e imprime o status e as alternativas. Para
usar outro arquivo:

```bash
python -m gradeia caminho/para/dataset.json
```

Uma execução bem-sucedida da grade básica termina com
`Status: CENARIO_VIAVEL` e até cinco soluções, cada uma com:

- quantidade de alterações
- professores afetados
- aulas deslocadas
- janelas criadas
- a lista das aulas que mudaram em relação à grade base

Exemplo de cabeçalho da saída:

```text
Dataset: dados/grade-basica.json
Aulas na grade base: 27
Professor ausente: PROFESSOR_ANA
Status: CENARIO_VIAVEL
Soluções: 5
```

Outros status possíveis:

- `ERRO_VALIDACAO` — alguma aula aponta para professor, turma,
  disciplina, dia ou período que não existe na grade
- `CENARIO_INVIAVEL` — a janela não cobre as aulas da ausência, ou o
  solver não achou alternativa válida

## Como editar o dataset

Abra `dados/grade-basica.json` e ajuste `aulas` ou `cenario`. A
disponibilidade de um professor aceita `"todos"` ou uma lista de pares
`[dia, periodo]`.

O cenário declara `idProfessor` e `turno`. Sem restrição extra, só
aquele turno pode mudar. `JANELA_DE_ALTERACAO` continua opcional: se
vier, precisa cobrir as aulas afetadas.

## Testes automatizados

Com o ambiente ativado:

```bash
pytest tests
```

A suíte cobre validação, restrições do solver, comparação das
soluções e um fumaça do dataset básico
(`tests/cenarios/test_dataset_basico.py`).

## Como chamar o motor no código

```python
from pathlib import Path

from gradeia.modules.cenarios.carregar_dataset import carregar_simulacao
from gradeia.modules.scheduling import OrToolsSchedulingEngine

grade_base, cenario = carregar_simulacao(Path("dados/grade-basica.json"))
resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)
print(resultado.status, len(resultado.solucoes))
```

`GradeBase` não é modificada. As soluções são propostas derivadas,
não a grade oficial.
