"""Interpretador para a linguagem Diamante"""

import sys
from typing import Any, Dict, List, Optional
from lexer import Lexer
from parser import Parser, (
    ASTNode, Programa, Numero, String, Booleano, Nulo, Identificador,
    BinOp, UnOp, Atribuicao, FuncaoDecl, ChamadaFuncao, Retorno,
    Se, Enquanto, Para, Importar, ImportarDe, Lista, Dicionario,
    AcessoAtributo, AcessoIndice
)


class RetornoExcecao(Exception):
    """Exceção para retorno de função"""
    def __init__(self, valor):
        self.valor = valor


class QuebraExcecao(Exception):
    """Exceção para break"""
    pass


class ContinuaExcecao(Exception):
    """Exceção para continue"""
    pass


class Funcao:
    """Representa uma função na linguagem"""
    def __init__(self, nome: str, parametros: List[str], corpo: List[ASTNode], escopo: Dict[str, Any]):
        self.nome = nome
        self.parametros = parametros
        self.corpo = corpo
        self.escopo = escopo
    
    def __repr__(self):
        return f"<funcao {self.nome}>"


class Interpretador:
    """Interpretador da linguagem Diamante"""
    
    def __init__(self):
        self.variaveis_globais: Dict[str, Any] = {}
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Configura funções nativas"""
        self.variaveis_globais['imprimir'] = self._builtin_imprimir
        self.variaveis_globais['entrada'] = self._builtin_entrada
        self.variaveis_globais['comprimento'] = self._builtin_comprimento
        self.variaveis_globais['tipo'] = self._builtin_tipo
        self.variaveis_globais['intervalo'] = self._builtin_intervalo
        self.variaveis_globais['mapa'] = self._builtin_mapa
        self.variaveis_globais['filtro'] = self._builtin_filtro
    
    def interpretar(self, codigo: str):
        """Interpreta o código Diamante"""
        # Lexer
        lexer = Lexer(codigo)
        tokens = lexer.tokenizar()
        
        # Parser
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Avaliação
        try:
            self._avaliar(ast, self.variaveis_globais)
        except RetornoExcecao:
            raise RuntimeError("Retorno fora de função")
    
    def _avaliar(self, node: ASTNode, variaveis: Dict[str, Any]) -> Any:
        """Avalia um nó da AST"""
        if isinstance(node, Programa):
            resultado = None
            for stmt in node.statements:
                resultado = self._avaliar(stmt, variaveis)
            return resultado
        
        elif isinstance(node, Numero):
            return node.valor
        
        elif isinstance(node, String):
            return node.valor
        
        elif isinstance(node, Booleano):
            return node.valor
        
        elif isinstance(node, Nulo):
            return None
        
        elif isinstance(node, Identificador):
            if node.nome in variaveis:
                return variaveis[node.nome]
            elif node.nome in self.variaveis_globais:
                return self.variaveis_globais[node.nome]
            else:
                raise NameError(f"Variável '{node.nome}' não definida")
        
        elif isinstance(node, Lista):
            return [self._avaliar(elem, variaveis) for elem in node.elementos]
        
        elif isinstance(node, Dicionario):
            resultado = {}
            for chave_node, valor_node in node.pares:
                chave = self._avaliar(chave_node, variaveis)
                valor = self._avaliar(valor_node, variaveis)
                resultado[chave] = valor
            return resultado
        
        elif isinstance(node, BinOp):
            return self._avaliar_binop(node, variaveis)
        
        elif isinstance(node, UnOp):
            return self._avaliar_unop(node, variaveis)
        
        elif isinstance(node, Atribuicao):
            valor = self._avaliar(node.valor, variaveis)
            variaveis[node.alvo] = valor
            return valor
        
        elif isinstance(node, FuncaoDecl):
            funcao = Funcao(node.nome, node.parametros, node.corpo, variaveis.copy())
            variaveis[node.nome] = funcao
            self.variaveis_globais[node.nome] = funcao
            return funcao
        
        elif isinstance(node, ChamadaFuncao):
            return self._chamar_funcao(node, variaveis)
        
        elif isinstance(node, Retorno):
            valor = None
            if node.valor:
                valor = self._avaliar(node.valor, variaveis)
            raise RetornoExcecao(valor)
        
        elif isinstance(node, Se):
            condicao = self._avaliar(node.condicao, variaveis)
            if self._eh_verdadeiro(condicao):
                resultado = None
                for stmt in node.corpo:
                    resultado = self._avaliar(stmt, variaveis)
                return resultado
            elif node.senao_corpo:
                resultado = None
                for stmt in node.senao_corpo:
                    resultado = self._avaliar(stmt, variaveis)
                return resultado
            return None
        
        elif isinstance(node, Enquanto):
            resultado = None
            while self._eh_verdadeiro(self._avaliar(node.condicao, variaveis)):
                try:
                    for stmt in node.corpo:
                        resultado = self._avaliar(stmt, variaveis)
                except QuebraExcecao:
                    break
                except ContinuaExcecao:
                    continue
            return resultado
        
        elif isinstance(node, Para):
            iteravel = self._avaliar(node.iteravel, variaveis)
            resultado = None
            try:
                for item in iteravel:
                    variaveis[node.variavel] = item
                    for stmt in node.corpo:
                        resultado = self._avaliar(stmt, variaveis)
            except QuebraExcecao:
                pass
            except ContinuaExcecao:
                pass
            return resultado
        
        elif isinstance(node, AcessoAtributo):
            obj = self._avaliar(node.objeto, variaveis)
            # Implementação simplificada
            if isinstance(obj, dict):
                return obj.get(node.atributo)
            else:
                raise AttributeError(f"Objeto não tem atributo '{node.atributo}'")
        
        elif isinstance(node, AcessoIndice):
            obj = self._avaliar(node.objeto, variaveis)
            indice = self._avaliar(node.indice, variaveis)
            try:
                return obj[indice]
            except (KeyError, IndexError, TypeError) as e:
                raise TypeError(f"Erro ao acessar índice: {e}")
        
        else:
            raise NotImplementedError(f"Nó não implementado: {type(node).__name__}")
    
    def _avaliar_binop(self, node: BinOp, variaveis: Dict[str, Any]) -> Any:
        """Avalia operação binária"""
        esquerda = self._avaliar(node.esquerda, variaveis)
        direita = self._avaliar(node.direita, variaveis)
        
        operador = node.operador
        
        # Aritméticos
        if operador == '+':
            return esquerda + direita
        elif operador == '-':
            return esquerda - direita
        elif operador == '*':
            return esquerda * direita
        elif operador == '/':
            return esquerda / direita
        elif operador == '//':
            return esquerda // direita
        elif operador == '%':
            return esquerda % direita
        elif operador == '**':
            return esquerda ** direita
        
        # Comparação
        elif operador == '==':
            return esquerda == direita
        elif operador == '!=':
            return esquerda != direita
        elif operador == '>':
            return esquerda > direita
        elif operador == '<':
            return esquerda < direita
        elif operador == '>=':
            return esquerda >= direita
        elif operador == '<=':
            return esquerda <= direita
        
        # Lógicos
        elif operador == 'e':
            return esquerda and direita
        elif operador == 'ou':
            return esquerda or direita
        
        else:
            raise ValueError(f"Operador desconhecido: {operador}")
    
    def _avaliar_unop(self, node: UnOp, variaveis: Dict[str, Any]) -> Any:
        """Avalia operação unária"""
        operando = self._avaliar(node.operando, variaveis)
        
        if node.operador == '-':
            return -operando
        elif node.operador == 'nao':
            return not self._eh_verdadeiro(operando)
        else:
            raise ValueError(f"Operador unário desconhecido: {node.operador}")
    
    def _chamar_funcao(self, node: ChamadaFuncao, variaveis: Dict[str, Any]) -> Any:
        """Executa uma chamada de função"""
        funcao_node = self._avaliar(node.nome, variaveis)
        args = [self._avaliar(arg, variaveis) for arg in node.argumentos]
        
        # Função nativa
        if callable(funcao_node):
            return funcao_node(*args)
        
        # Função definida
        elif isinstance(funcao_node, Funcao):
            if len(args) != len(funcao_node.parametros):
                raise TypeError(f"Função {funcao_node.nome} espera {len(funcao_node.parametros)} argumentos, mas recebeu {len(args)}")
            
            # Novo escopo
            novo_escopo = funcao_node.escopo.copy()
            for param, arg in zip(funcao_node.parametros, args):
                novo_escopo[param] = arg
            
            try:
                resultado = None
                for stmt in funcao_node.corpo:
                    resultado = self._avaliar(stmt, novo_escopo)
                return resultado
            except RetornoExcecao as e:
                return e.valor
        
        else:
            raise TypeError(f"'{type(funcao_node).__name__}' não é chamável")
    
    def _eh_verdadeiro(self, valor: Any) -> bool:
        """Verifica se um valor é "verdadeiro" (truthy)"""
        if valor is None or valor is False:
            return False
        if valor == 0 or valor == "" or valor == [] or valor == {}:
            return False
        return True
    
    # Funções nativas
    
    def _builtin_imprimir(self, *args):
        """Função nativa: imprimir"""
        texto = " ".join(str(arg) for arg in args)
        print(texto)
        return None
    
    def _builtin_entrada(self, prompt=""):
        """Função nativa: entrada"""
        return input(str(prompt))
    
    def _builtin_comprimento(self, obj):
        """Função nativa: comprimento"""
        return len(obj)
    
    def _builtin_tipo(self, obj):
        """Função nativa: tipo"""
        if isinstance(obj, bool):
            return "booleano"
        elif isinstance(obj, int):
            return "numero"
        elif isinstance(obj, float):
            return "numero"
        elif isinstance(obj, str):
            return "string"
        elif isinstance(obj, list):
            return "lista"
        elif isinstance(obj, dict):
            return "dicionario"
        elif obj is None:
            return "nulo"
        else:
            return "desconhecido"
    
    def _builtin_intervalo(self, *args):
        """Função nativa: intervalo (range)"""
        if len(args) == 1:
            return list(range(int(args[0])))
        elif len(args) == 2:
            return list(range(int(args[0]), int(args[1])))
        elif len(args) == 3:
            return list(range(int(args[0]), int(args[1]), int(args[2])))
        else:
            raise TypeError(f"intervalo() espera 1-3 argumentos, mas recebeu {len(args)}")
    
    def _builtin_mapa(self, funcao, iteravel):
        """Função nativa: mapa"""
        resultado = []
        for item in iteravel:
            if isinstance(funcao, Funcao):
                try:
                    novo_escopo = funcao.escopo.copy()
                    novo_escopo[funcao.parametros[0]] = item
                    res = None
                    for stmt in funcao.corpo:
                        res = self._avaliar(stmt, novo_escopo)
                    resultado.append(res)
                except RetornoExcecao as e:
                    resultado.append(e.valor)
            else:
                resultado.append(funcao(item))
        return resultado
    
    def _builtin_filtro(self, funcao, iteravel):
        """Função nativa: filtro"""
        resultado = []
        for item in iteravel:
            if isinstance(funcao, Funcao):
                try:
                    novo_escopo = funcao.escopo.copy()
                    novo_escopo[funcao.parametros[0]] = item
                    res = None
                    for stmt in funcao.corpo:
                        res = self._avaliar(stmt, novo_escopo)
                    if self._eh_verdadeiro(res):
                        resultado.append(item)
                except RetornoExcecao as e:
                    if self._eh_verdadeiro(e.valor):
                        resultado.append(item)
            else:
                if self._eh_verdadeiro(funcao(item)):
                    resultado.append(item)
        return resultado


def main():
    if len(sys.argv) < 2:
        print("Uso: python interpreter.py <arquivo.diamante>")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        interpretador = Interpretador()
        interpretador.interpretar(codigo)
    
    except FileNotFoundError:
        print(f"Erro: arquivo '{arquivo}' não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
