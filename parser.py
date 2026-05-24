"""Parser para a linguagem Diamante"""

from dataclasses import dataclass
from typing import List, Optional, Union
from lexer import Token, TokenType, Lexer


# AST Node Types
@dataclass
class ASTNode:
    pass


@dataclass
class Programa(ASTNode):
    statements: List[ASTNode]


@dataclass
class Numero(ASTNode):
    valor: float


@dataclass
class String(ASTNode):
    valor: str


@dataclass
class Booleano(ASTNode):
    valor: bool


@dataclass
class Nulo(ASTNode):
    pass


@dataclass
class Identificador(ASTNode):
    nome: str


@dataclass
class BinOp(ASTNode):
    esquerda: ASTNode
    operador: str
    direita: ASTNode


@dataclass
class UnOp(ASTNode):
    operador: str
    operando: ASTNode


@dataclass
class Atribuicao(ASTNode):
    alvo: str
    valor: ASTNode


@dataclass
class FuncaoDecl(ASTNode):
    nome: str
    parametros: List[str]
    corpo: List[ASTNode]


@dataclass
class ChamadaFuncao(ASTNode):
    nome: ASTNode
    argumentos: List[ASTNode]


@dataclass
class Retorno(ASTNode):
    valor: Optional[ASTNode] = None


@dataclass
class Se(ASTNode):
    condicao: ASTNode
    corpo: List[ASTNode]
    senao_corpo: Optional[List[ASTNode]] = None


@dataclass
class Enquanto(ASTNode):
    condicao: ASTNode
    corpo: List[ASTNode]


@dataclass
class Para(ASTNode):
    variavel: str
    iteravel: ASTNode
    corpo: List[ASTNode]


@dataclass
class Importar(ASTNode):
    modulo: str
    apelido: Optional[str] = None


@dataclass
class ImportarDe(ASTNode):
    modulo: str
    itens: List[tuple]  # [(nome, apelido), ...]


@dataclass
class Lista(ASTNode):
    elementos: List[ASTNode]


@dataclass
class Dicionario(ASTNode):
    pares: List[tuple]  # [(chave, valor), ...]


@dataclass
class AcessoAtributo(ASTNode):
    objeto: ASTNode
    atributo: str


@dataclass
class AcessoIndice(ASTNode):
    objeto: ASTNode
    indice: ASTNode


class Parser:
    """Parser para a linguagem Diamante"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicao = 0
    
    def parse(self) -> Programa:
        """Faz o parse do programa completo"""
        statements = []
        
        # Pula quebras de linha iniciais
        self._pular_quebras_linha()
        
        # Espera pela tag <diamante>
        if not self._verificar(TokenType.DIAMANTE_INICIO):
            raise SyntaxError(f"Esperado <diamante> no início do arquivo")
        
        self._avancar()
        self._pular_quebras_linha()
        
        # Parse dos statements
        while not self._verificar(TokenType.DIAMANTE_FIM) and not self._verificar(TokenType.EOF):
            if self._verificar(TokenType.QUEBRA_LINHA):
                self._avancar()
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        # Espera pela tag </diamante>
        if not self._verificar(TokenType.DIAMANTE_FIM):
            raise SyntaxError(f"Esperado </diamante> no final do arquivo")
        
        return Programa(statements)
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Faz o parse de um statement"""
        self._pular_quebras_linha()
        
        if self._verificar(TokenType.FUNCAO):
            return self._parse_funcao()
        elif self._verificar(TokenType.SE):
            return self._parse_se()
        elif self._verificar(TokenType.ENQUANTO):
            return self._parse_enquanto()
        elif self._verificar(TokenType.PARA):
            return self._parse_para()
        elif self._verificar(TokenType.RETORNAR):
            return self._parse_retorno()
        elif self._verificar(TokenType.IMPORTAR):
            return self._parse_importar()
        elif self._verificar(TokenType.DE):
            return self._parse_importar_de()
        else:
            return self._parse_expressao_statement()
    
    def _parse_expressao_statement(self) -> Optional[ASTNode]:
        """Parse de statement que é uma expressão"""
        expr = self._parse_expressao()
        self._pular_quebras_linha()
        return expr
    
    def _parse_expressao(self) -> ASTNode:
        """Parse de uma expressão"""
        return self._parse_atribuicao()
    
    def _parse_atribuicao(self) -> ASTNode:
        """Parse de atribuição"""
        expr = self._parse_ou()
        
        if self._verificar(TokenType.ATRIBUIR):
            self._avancar()
            valor = self._parse_atribuicao()
            if isinstance(expr, Identificador):
                return Atribuicao(expr.nome, valor)
            else:
                raise SyntaxError("Alvo de atribuição inválido")
        
        return expr
    
    def _parse_ou(self) -> ASTNode:
        """Parse de operador OU"""
        esquerda = self._parse_e()
        
        while self._verificar(TokenType.OU):
            operador = self._token_atual().valor
            self._avancar()
            direita = self._parse_e()
            esquerda = BinOp(esquerda, operador, direita)
        
        return esquerda
    
    def _parse_e(self) -> ASTNode:
        """Parse de operador E"""
        esquerda = self._parse_comparacao()
        
        while self._verificar(TokenType.E):
            operador = self._token_atual().valor
            self._avancar()
            direita = self._parse_comparacao()
            esquerda = BinOp(esquerda, operador, direita)
        
        return esquerda
    
    def _parse_comparacao(self) -> ASTNode:
        """Parse de operador de comparação"""
        esquerda = self._parse_termo()
        
        tipos_comparacao = [
            TokenType.IGUAL, TokenType.DIFERENTE, TokenType.MAIOR,
            TokenType.MENOR, TokenType.MAIOR_IGUAL, TokenType.MENOR_IGUAL
        ]
        
        while any(self._verificar(t) for t in tipos_comparacao):
            operador = self._token_atual().valor
            self._avancar()
            direita = self._parse_termo()
            esquerda = BinOp(esquerda, operador, direita)
        
        return esquerda
    
    def _parse_termo(self) -> ASTNode:
        """Parse de adição e subtração"""
        esquerda = self._parse_fator()
        
        while self._verificar(TokenType.MAIS) or self._verificar(TokenType.MENOS):
            operador = self._token_atual().valor
            self._avancar()
            direita = self._parse_fator()
            esquerda = BinOp(esquerda, operador, direita)
        
        return esquerda
    
    def _parse_fator(self) -> ASTNode:
        """Parse de multiplicação, divisão e módulo"""
        esquerda = self._parse_potencia()
        
        tipos_multiplicacao = [TokenType.MULTIPLICAR, TokenType.DIVIDIR, TokenType.DIVISAO_INTEIRA, TokenType.MODULO]
        
        while any(self._verificar(t) for t in tipos_multiplicacao):
            operador = self._token_atual().valor
            self._avancar()
            direita = self._parse_potencia()
            esquerda = BinOp(esquerda, operador, direita)
        
        return esquerda
    
    def _parse_potencia(self) -> ASTNode:
        """Parse de potenciação (direita associativa)"""
        esquerda = self._parse_unaria()
        
        if self._verificar(TokenType.POTENCIA):
            operador = self._token_atual().valor
            self._avancar()
            direita = self._parse_potencia()  # Associativa à direita
            return BinOp(esquerda, operador, direita)
        
        return esquerda
    
    def _parse_unaria(self) -> ASTNode:
        """Parse de operadores unários"""
        if self._verificar(TokenType.NAO) or self._verificar(TokenType.MENOS):
            operador = self._token_atual().valor
            self._avancar()
            operando = self._parse_unaria()
            return UnOp(operador, operando)
        
        return self._parse_pos_fixa()
    
    def _parse_pos_fixa(self) -> ASTNode:
        """Parse de expressões pós-fixas (chamadas, acesso)"""
        expr = self._parse_primaria()
        
        while True:
            if self._verificar(TokenType.PAREN_ESQUERDA):
                # Chamada de função
                self._avancar()
                argumentos = []
                
                if not self._verificar(TokenType.PAREN_DIREITA):
                    argumentos.append(self._parse_expressao())
                    while self._verificar(TokenType.VIRGULA):
                        self._avancar()
                        argumentos.append(self._parse_expressao())
                
                if not self._verificar(TokenType.PAREN_DIREITA):
                    raise SyntaxError("Esperado ')' após argumentos")
                self._avancar()
                expr = ChamadaFuncao(expr, argumentos)
            
            elif self._verificar(TokenType.PONTO):
                # Acesso a atributo
                self._avancar()
                if not self._verificar(TokenType.IDENTIFICADOR):
                    raise SyntaxError("Esperado identificador após '.")
                atributo = self._token_atual().valor
                self._avancar()
                expr = AcessoAtributo(expr, atributo)
            
            elif self._verificar(TokenType.COLCHETE_ESQUERDA):
                # Acesso a índice
                self._avancar()
                indice = self._parse_expressao()
                if not self._verificar(TokenType.COLCHETE_DIREITA):
                    raise SyntaxError("Esperado ']' após índice")
                self._avancar()
                expr = AcessoIndice(expr, indice)
            else:
                break
        
        return expr
    
    def _parse_primaria(self) -> ASTNode:
        """Parse de expressão primária"""
        if self._verificar(TokenType.NUMERO):
            valor = self._token_atual().valor
            self._avancar()
            return Numero(valor)
        
        elif self._verificar(TokenType.STRING):
            valor = self._token_atual().valor
            self._avancar()
            return String(valor)
        
        elif self._verificar(TokenType.VERDADEIRO):
            self._avancar()
            return Booleano(True)
        
        elif self._verificar(TokenType.FALSO):
            self._avancar()
            return Booleano(False)
        
        elif self._verificar(TokenType.NULO):
            self._avancar()
            return Nulo()
        
        elif self._verificar(TokenType.IDENTIFICADOR):
            nome = self._token_atual().valor
            self._avancar()
            return Identificador(nome)
        
        elif self._verificar(TokenType.PAREN_ESQUERDA):
            self._avancar()
            expr = self._parse_expressao()
            if not self._verificar(TokenType.PAREN_DIREITA):
                raise SyntaxError("Esperado ')' após expressão")
            self._avancar()
            return expr
        
        elif self._verificar(TokenType.COLCHETE_ESQUERDA):
            return self._parse_lista()
        
        elif self._verificar(TokenType.CHAVE_ESQUERDA):
            return self._parse_dicionario()
        
        elif self._verificar(TokenType.LAMBDA):
            return self._parse_lambda()
        
        else:
            raise SyntaxError(f"Token inesperado: {self._token_atual()}")
    
    def _parse_lista(self) -> Lista:
        """Parse de uma lista"""
        self._avancar()  # [
        elementos = []
        
        if not self._verificar(TokenType.COLCHETE_DIREITA):
            elementos.append(self._parse_expressao())
            while self._verificar(TokenType.VIRGULA):
                self._avancar()
                if self._verificar(TokenType.COLCHETE_DIREITA):
                    break
                elementos.append(self._parse_expressao())
        
        if not self._verificar(TokenType.COLCHETE_DIREITA):
            raise SyntaxError("Esperado ']' para fechar lista")
        self._avancar()
        
        return Lista(elementos)
    
    def _parse_dicionario(self) -> Dicionario:
        """Parse de um dicionário"""
        self._avancar()  # {
        pares = []
        
        if not self._verificar(TokenType.CHAVE_DIREITA):
            # Primeiro par
            chave = self._parse_expressao()
            if not self._verificar(TokenType.DOIS_PONTOS):
                raise SyntaxError("Esperado ':' em dicionário")
            self._avancar()
            valor = self._parse_expressao()
            pares.append((chave, valor))
            
            while self._verificar(TokenType.VIRGULA):
                self._avancar()
                if self._verificar(TokenType.CHAVE_DIREITA):
                    break
                chave = self._parse_expressao()
                if not self._verificar(TokenType.DOIS_PONTOS):
                    raise SyntaxError("Esperado ':' em dicionário")
                self._avancar()
                valor = self._parse_expressao()
                pares.append((chave, valor))
        
        if not self._verificar(TokenType.CHAVE_DIREITA):
            raise SyntaxError("Esperado '}' para fechar dicionário")
        self._avancar()
        
        return Dicionario(pares)
    
    def _parse_lambda(self) -> 'Lambda':
        """Parse de uma função lambda"""
        # Implementar depois
        raise NotImplementedError("Lambda não implementado ainda")
    
    def _parse_funcao(self) -> FuncaoDecl:
        """Parse de declaração de função"""
        self._avancar()  # funcao
        
        if not self._verificar(TokenType.IDENTIFICADOR):
            raise SyntaxError("Esperado nome de função")
        nome = self._token_atual().valor
        self._avancar()
        
        if not self._verificar(TokenType.PAREN_ESQUERDA):
            raise SyntaxError("Esperado '(' após nome da função")
        self._avancar()
        
        parametros = []
        if not self._verificar(TokenType.PAREN_DIREITA):
            parametros.append(self._token_atual().valor)
            self._avancar()
            while self._verificar(TokenType.VIRGULA):
                self._avancar()
                parametros.append(self._token_atual().valor)
                self._avancar()
        
        if not self._verificar(TokenType.PAREN_DIREITA):
            raise SyntaxError("Esperado ')' após parâmetros")
        self._avancar()
        
        if not self._verificar(TokenType.DOIS_PONTOS):
            raise SyntaxError("Esperado ':' após assinatura de função")
        self._avancar()
        
        self._pular_quebras_linha()
        corpo = self._parse_bloco()
        
        return FuncaoDecl(nome, parametros, corpo)
    
    def _parse_se(self) -> Se:
        """Parse de statement if"""
        self._avancar()  # se
        
        if not self._verificar(TokenType.PAREN_ESQUERDA):
            raise SyntaxError("Esperado '(' após 'se'")
        self._avancar()
        
        condicao = self._parse_expressao()
        
        if not self._verificar(TokenType.PAREN_DIREITA):
            raise SyntaxError("Esperado ')' após condição")
        self._avancar()
        
        if not self._verificar(TokenType.DOIS_PONTOS):
            raise SyntaxError("Esperado ':' após condição")
        self._avancar()
        
        self._pular_quebras_linha()
        corpo = self._parse_bloco()
        
        senao_corpo = None
        if self._verificar(TokenType.SENAO):
            self._avancar()
            if not self._verificar(TokenType.DOIS_PONTOS):
                raise SyntaxError("Esperado ':' após 'senao'")
            self._avancar()
            self._pular_quebras_linha()
            senao_corpo = self._parse_bloco()
        
        return Se(condicao, corpo, senao_corpo)
    
    def _parse_enquanto(self) -> Enquanto:
        """Parse de statement while"""
        self._avancar()  # enquanto
        
        if not self._verificar(TokenType.PAREN_ESQUERDA):
            raise SyntaxError("Esperado '(' após 'enquanto'")
        self._avancar()
        
        condicao = self._parse_expressao()
        
        if not self._verificar(TokenType.PAREN_DIREITA):
            raise SyntaxError("Esperado ')' após condição")
        self._avancar()
        
        if not self._verificar(TokenType.DOIS_PONTOS):
            raise SyntaxError("Esperado ':' após condição")
        self._avancar()
        
        self._pular_quebras_linha()
        corpo = self._parse_bloco()
        
        return Enquanto(condicao, corpo)
    
    def _parse_para(self) -> Para:
        """Parse de statement for"""
        self._avancar()  # para
        
        if not self._verificar(TokenType.IDENTIFICADOR):
            raise SyntaxError("Esperado identificador em 'para'")
        variavel = self._token_atual().valor
        self._avancar()
        
        if not self._verificar(TokenType.EM):
            raise SyntaxError("Esperado 'em' em loop 'para'")
        self._avancar()
        
        iteravel = self._parse_expressao()
        
        if not self._verificar(TokenType.DOIS_PONTOS):
            raise SyntaxError("Esperado ':' após iterável")
        self._avancar()
        
        self._pular_quebras_linha()
        corpo = self._parse_bloco()
        
        return Para(variavel, iteravel, corpo)
    
    def _parse_retorno(self) -> Retorno:
        """Parse de statement return"""
        self._avancar()  # retornar
        
        valor = None
        if not self._verificar(TokenType.QUEBRA_LINHA) and not self._verificar(TokenType.EOF):
            valor = self._parse_expressao()
        
        return Retorno(valor)
    
    def _parse_importar(self) -> Importar:
        """Parse de 'importar modulo'"""
        self._avancar()  # importar
        
        if not self._verificar(TokenType.IDENTIFICADOR):
            raise SyntaxError("Esperado nome do módulo")
        modulo = self._token_atual().valor
        self._avancar()
        
        apelido = None
        if self._verificar(TokenType.COMO):
            self._avancar()
            if not self._verificar(TokenType.IDENTIFICADOR):
                raise SyntaxError("Esperado nome após 'como'")
            apelido = self._token_atual().valor
            self._avancar()
        
        return Importar(modulo, apelido)
    
    def _parse_importar_de(self) -> ImportarDe:
        """Parse de 'de modulo importar ...'"""
        self._avancar()  # de
        
        if not self._verificar(TokenType.IDENTIFICADOR):
            raise SyntaxError("Esperado nome do módulo após 'de'")
        modulo = self._token_atual().valor
        self._avancar()
        
        if not self._verificar(TokenType.IMPORTAR):
            raise SyntaxError("Esperado 'importar' após nome do módulo")
        self._avancar()
        
        itens = []
        
        if self._verificar(TokenType.MULTIPLICAR):
            # Importar tudo
            self._avancar()
            itens.append(('*', None))
        else:
            if not self._verificar(TokenType.IDENTIFICADOR):
                raise SyntaxError("Esperado identificador após 'importar'")
            nome = self._token_atual().valor
            self._avancar()
            
            apelido = None
            if self._verificar(TokenType.COMO):
                self._avancar()
                if not self._verificar(TokenType.IDENTIFICADOR):
                    raise SyntaxError("Esperado nome após 'como'")
                apelido = self._token_atual().valor
                self._avancar()
            
            itens.append((nome, apelido))
            
            while self._verificar(TokenType.VIRGULA):
                self._avancar()
                if not self._verificar(TokenType.IDENTIFICADOR):
                    raise SyntaxError("Esperado identificador após vírgula")
                nome = self._token_atual().valor
                self._avancar()
                
                apelido = None
                if self._verificar(TokenType.COMO):
                    self._avancar()
                    if not self._verificar(TokenType.IDENTIFICADOR):
                        raise SyntaxError("Esperado nome após 'como'")
                    apelido = self._token_atual().valor
                    self._avancar()
                
                itens.append((nome, apelido))
        
        return ImportarDe(modulo, itens)
    
    def _parse_bloco(self) -> List[ASTNode]:
        """Parse de um bloco de código indentado"""
        statements = []
        
        while not self._verificar(TokenType.EOF) and not self._verificar(TokenType.DIAMANTE_FIM):
            if self._verificar(TokenType.QUEBRA_LINHA):
                self._avancar()
                continue
            
            # Simples verificação para fim de bloco (para-enquanto-senao)
            if self._verificar(TokenType.SENAO) or self._verificar(TokenType.SENAO_SE):
                break
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _pular_quebras_linha(self):
        """Pula quebras de linha"""
        while self._verificar(TokenType.QUEBRA_LINHA):
            self._avancar()
    
    def _verificar(self, tipo: TokenType) -> bool:
        """Verifica se o token atual é do tipo especificado"""
        if self.posicao >= len(self.tokens):
            return False
        return self.tokens[self.posicao].tipo == tipo
    
    def _token_atual(self) -> Token:
        """Retorna o token atual"""
        if self.posicao >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.posicao]
    
    def _avancar(self) -> Token:
        """Avança para o próximo token"""
        token = self._token_atual()
        if self.posicao < len(self.tokens):
            self.posicao += 1
        return token
