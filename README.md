# Diamante 💎

Uma linguagem de programação híbrida que combina a elegância do **Python** com a flexibilidade do **JavaScript**.

## Características

- 🐍 Sintaxe inspirada em Python (clean e legível)
- ⚡ Dinamismo do JavaScript
- 📦 Sistema robusto de imports
- 🔧 Tipagem dinâmica
- 🎯 Fácil de aprender e usar

## Extensão

Todos os arquivos Diamante usam a extensão `.diamante`

## Estrutura do Projeto

```
diamante-/
├── README.md           # Este arquivo
├── spec.md            # Especificação da linguagem
├── lexer.py           # Tokenizador
├── parser.py          # Parser
├── interpreter.py     # Interpretador
├── exemplo.diamante   # Exemplos de código
└── stdlib/            # Biblioteca padrão
```

## Instalação

```bash
git clone https://github.com/gustavohenriquecosta86-cloud/diamante-.git
cd diamante-
python interpreter.py seu_arquivo.diamante
```

## Exemplos

### Hello World

```diamante
<diamante>
imprimir("Olá, Diamante!")
</diamante>
```

### Variáveis e Tipos

```diamante
<diamante>
nome = "Gustavo"
idade = 25
altura = 1.80
ativo = verdadeiro

imprimir(nome)
imprimir(idade)
</diamante>
```

### Funções

```diamante
<diamante>
funcao saudar(nome):
    retornar "Olá, " + nome

resultado = saudar("Mundo")
imprimir(resultado)
</diamante>
```

### Imports

```diamante
<diamante>
importar math
de utils importar calcular_imc

area = math.pi * 5 ** 2
imc = calcular_imc(70, 1.80)
</diamante>
```

## Roadmap

- [x] Especificação básica
- [ ] Lexer completo
- [ ] Parser AST
- [ ] Interpretador funcional
- [ ] Sistema de imports
- [ ] Biblioteca padrão
- [ ] Testes
- [ ] Documentação completa

## Licença

MIT

## Autor

Gustavo Henrique Costa