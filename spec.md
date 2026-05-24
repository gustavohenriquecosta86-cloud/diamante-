# Especificação da Linguagem Diamante v0.1

## 1. Bloco de Código

Todos os arquivos `.diamante` devem estar envolvidos em tags:

```diamante
<diamante>
  # código aqui
</diamante>
```

## 2. Comentários

```diamante
<diamante>
# Comentário de linha única

"""
Comentário de múltiplas linhas
Pode ocupar várias linhas
"""
</diamante>
```

## 3. Tipos de Dados

### Primitivos
- **Número**: `42`, `3.14`
- **String**: `"texto"` ou `'texto'`
- **Booleano**: `verdadeiro`, `falso`
- **Nulo**: `nulo`

### Coleções
- **Lista**: `[1, 2, 3]`
- **Dicionário**: `{"chave": "valor"}`
- **Tupla**: `(1, 2, 3)`
- **Conjunto**: `{1, 2, 3}`

## 4. Variáveis

```diamante
<diamante>
variavel = 10
outro_nome = "texto"
</diamante>
```

## 5. Operadores

### Aritméticos
- `+` Adição
- `-` Subtração
- `*` Multiplicação
- `/` Divisão
- `//` Divisão inteira
- `%` Módulo
- `**` Exponenciação

### Comparação
- `==` Igual
- `!=` Diferente
- `>` Maior que
- `<` Menor que
- `>=` Maior ou igual
- `<=` Menor ou igual

### Lógicos
- `e` AND
- `ou` OR
- `nao` NOT

### Atribuição
- `=` Atribuição simples
- `+=` Adição e atribuição
- `-=` Subtração e atribuição
- `*=` Multiplicação e atribuição
- `/=` Divisão e atribuição

## 6. Controle de Fluxo

### Condicional

```diamante
<diamante>
se (condicao):
    # código
senao_se (outra_condicao):
    # código
senao:
    # código
</diamante>
```

### Loops

```diamante
<diamante>
# While
enquanto (condicao):
    # código
    interromper  # break
    continuar    # continue

# For
para i em intervalo(10):
    # código

para item em lista:
    # código
</diamante>
```

## 7. Funções

```diamante
<diamante>
funcao nome_da_funcao(parametro1, parametro2):
    # código
    retornar resultado

# Chamada
resultado = nome_da_funcao(arg1, arg2)
</diamante>
```

### Funções Anônimas (Lambda)

```diamante
<diamante>
quadrado = lambda x: x ** 2
resultado = quadrado(5)  # 25
</diamante>
```

## 8. Sistema de Imports

### Importação Simples

```diamante
<diamante>
importar modulo
importar modulo como apelido
</diamante>
```

### Importação Específica

```diamante
<diamante>
de modulo importar funcao
de modulo importar funcao1, funcao2
de modulo importar funcao como novo_nome
de modulo importar *  # importa tudo
</diamante>
```

## 9. Classes (Futuro)

```diamante
<diamante>
classe Pessoa:
    funcao __init__(self, nome):
        self.nome = nome
    
    funcao saudar(self):
        retornar "Olá, " + self.nome
</diamante>
```

## 10. Exceções (Futuro)

```diamante
<diamante>
tente:
    # código
exceto Erro:
    # tratamento
finalmente:
    # limpeza
</diamante>
```

## 11. Funções Nativas

- `imprimir(...)` - Imprime no console
- `entrada(...)` - Lê entrada do usuário
- `comprimento(...)` - Retorna o comprimento
- `tipo(...)` - Retorna o tipo
- `intervalo(...)` - Cria uma sequência
- `mapa(...)` - Mapeia função sobre lista
- `filtro(...)` - Filtra lista
- `reduzir(...)` - Reduz lista a um valor

## 12. Módulos Internos

### math
- `math.pi`
- `math.raiz(x)`
- `math.potencia(x, y)`
- `math.absoluto(x)`

### string
- `string.maiusculas(s)`
- `string.minusculas(s)`
- `string.dividir(s, sep)`
- `string.juntar(lista, sep)`

### lista
- `lista.ordenar(l)`
- `lista.inverter(l)`
- `lista.adicionar(l, item)`
- `lista.remover(l, item)`
