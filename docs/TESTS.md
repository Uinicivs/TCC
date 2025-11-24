# Testes

## Testes de Verificação

- [1. Caso totalmente viável](#1-caso-totalmente-viável-sem-inconsistências-sem-reduções-sem-pruned)
- [2. Branch inconsistente (unsatisfiable)](#2-caso-com-branch-inconsistente-unsatisfiable)
- [3. Condição reduzível (redundant / simplificável)](#3-caso-com-condição-reduzível-redundant--simplificável)
- [4. Uncovered path (falta de tratativa)](#4-caso-com-uncovered-path-falta-de-tratativa)
- [5. Parcialmente contraditório (unsat only in context)](#5-caso-parcialmente-contraditório-unsat-only-in-context)
- [6. Múltiplas reduções em AND composto](#6-caso-com-múltiplas-reduções-dentro-de-um-and-composto)
- [7. Pruned no false-branch do IF](#7-caso-com-pruned-no-false-branch-do-if)
- [8. Nested inconsistency + nested reducibility](#8-caso-com-nested-inconsistency--nested-reducibility)

### 1. Caso totalmente viável (sem inconsistências, sem reduções, sem pruned)

Descrição: Árvore de decisão perfeita e mínima. Todas as condições são necessárias, todos os ramos são alcançáveis, não há redundâncias nem caminhos mortos. Representa o caso ideal: cobertura completa e determinística.

Link: `tests/1/`

Exemplo:

```
VARIABLES
x: number
--------------------------
PROGRAM
IF x >= 0:
	END 'ok'
ELSE:
	END 'negative'
```

---

### 2. Caso com branch inconsistente (unsatisfiable)

Descrição: Contém um ramo logicamente impossível. A condição `x > 10` torna `x < 5` falsa dentro do mesmo ramo — o nó `END 'impossible'` nunca será alcançado (dead branch).

Link: `tests/2/`

Exemplo:

```
VARIABLES
x: number
--------------------------
PROGRAM
IF x > 10:
	IF x < 5:
		END 'impossible'
	ELSE:
		END 'valid'
ELSE:
	END 'other'
```

---

### 3. Caso com condição reduzível (redundant / simplificável)

Descrição: Redundância contextual: dentro do ramo `age >= 18`, a condição `age >= 10` é sempre verdadeira e pode ser eliminada. O ramo `END 'error'` é inalcançável.

Link: `tests/3/`

Exemplo:

```
VARIABLES
age: number
--------------------------
PROGRAM
IF age >= 18:
	IF age >= 10:
		END 'adult'
	ELSE:
		END 'error'
ELSE:
	END 'minor'
```

---

### 4. Caso com uncovered path (falta de tratativa)

Descrição: Árvore incompleta: falta o ramo `ELSE` do IF raiz. Não há tratamento para alguns valores (ex.: `x = 5`), representando um espaço de entrada sem cobertura.

Link: `tests/4/`

Exemplo:

```
VARIABLES
x: number
--------------------------
PROGRAM
IF x > 10:
	IF x > 20:
		END 'greater_than_20'
	ELSE:
		END 'between_10_and_20'
```

---

### 5. Caso parcialmente contraditório (unsat only in context)

Descrição: Inconsistência contextual: a condição `age < 0` dentro do ramo `age >= 18` nunca pode ser verdadeira. O nó `END 'bad'` é inalcançável, mas a condição isolada não é globalmente contraditória.

Link: `tests/5/`

Exemplo:

```
VARIABLES
age: number
--------------------------
PROGRAM
IF age >= 18:
	IF age < 0:
		END 'bad'
	ELSE:
		END 'valid'
ELSE:
	END 'minor'
```

---

### 6. Caso com múltiplas reduções dentro de um AND composto

Descrição: Em `x > 10`, todas as condições do AND (`x > 5`, `x > 3`, `x > 0`) são subsumidas pela condição pai; a expressão pode ser reduzida a `true` no contexto. O ramo `END 'B'` é inalcançável.

Link: `tests/6/`

Exemplo:

```
VARIABLES
x: number
--------------------------
PROGRAM
IF x > 10:
	IF x > 5 and x > 3 and x > 0:
		END 'A'
	ELSE:
		END 'B'
ELSE:
	END 'C'
```

---

### 7. Caso com pruned no false-branch do if

Descrição: Pruning no false-branch: dentro do `ELSE` (quando `n >= 0`) a condição `n < 0` é sempre falsa — o ramo `END 'again_neg'` é inalcançável e pode ser removido.

Link: `tests/7/`

Exemplo:

```
VARIABLES
n: number
--------------------------
PROGRAM
IF n < 0:
	END 'neg'
ELSE:
	IF n < 0:
		END 'again_neg'
	ELSE:
		END 'non_neg'
```

---

### 8. Caso com nested inconsistency + nested reducibility

Descrição: Caso avançado com duas falhas aninhadas:

- Condição interna impossível: `score >= 0 and score < -5` → contradição global → `END 'bad'` inalcançável.
- Condição redundante no ELSE: `score >= 0` é redundante considerando o IF pai → `END 'error'` inalcançável.

Link: `tests/8/`

Exemplo:

```
VARIABLES
score: number
--------------------------
PROGRAM
IF score >= 0:
	IF score >= 0 and score < -5:
		END 'bad'
	ELSE:
		IF score >= 0:
			END 'good'
		ELSE:
			END 'error'
ELSE:
	END 'invalid'
```

---
