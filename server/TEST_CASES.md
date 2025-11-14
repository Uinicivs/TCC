## 1. Caso totalmente viável (sem inconsistências, sem reduções, sem pruned)

```bash
VARIABLES
x: number
--------------------------
PROGRAM
IF x >= 0:
    END 'ok'
ELSE:
    END 'negative'
```

## 2. Caso com branch inconsistente (unsatisfiable)

```bash
VARIABLES
x: number
--------------------------
PROGRAM
IF x > 10:
    IF x < 5: // impossibilidade: x > 10 AND x < 5
        END 'impossible'
    ELSE:
        END 'valid'
ELSE:
    END 'other'
```

## 3. Caso com condição reduzível (redundant / simplificável)

```bash
VARIABLES
age: number
--------------------------
PROGRAM
IF age >= 18:
    IF age >= 10: // redundant, “age >= 18” already implies it
        END 'adult'
    ELSE:
        END 'error'
ELSE:
    END 'minor'
```

## 4. Caso com uncovered path (falta de tratativa)

```bash
VARIABLES
x: number
--------------------------
PROGRAM
IF x > 10:
    IF x > 20:
        END 'greater_than_20'
    ELSE:
        END 'between_10_and_20'
//no ELSE here
```

## 5. Caso parcialmente contraditório (unsat only in context)

```bash
VARIABLES
age: number
--------------------------
PROGRAM
IF age >= 18:
    IF age < 0:  // unsat only under context: age >= 18
        END 'bad'
    ELSE:
        END 'valid'
ELSE:
    END 'minor'
```

## 6. Caso com múltiplas reduções dentro de um AND composto

```bash
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

## 7. Caso com pruned no false-branch do if

```bash
VARIABLES
n: number
--------------------------
PROGRAM
IF n < 0:
    END 'neg'
ELSE:
    IF n < 0: // false-branch contradiction under context
        END 'again_neg'
    ELSE:
        END 'non_neg'
```

## 8. Caso com nested inconsistency + nested reducibility

```bash
VARIABLES
score: number
--------------------------
PROGRAM
IF score >= 0:
    IF score >= 0 and score < -5: // inner contradiction
        END 'bad'
    ELSE:
        IF score >= 0:  // redundant
            END 'good'
        ELSE:
            END 'error'
ELSE:
    END 'invalid'
```
