"""Lexer (Tokenizador) para a linguagem Diamante"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Literais
    NUMERO = auto()
    STRING = auto()
    VERDADEIRO = auto()
    FALSO = auto()
    NULO = auto()
    
    # Identificadores e palavras-chave
    IDENTIFICADOR = auto()
    
    # Palavras-chave
    FUNCAO = auto()
    RETORNAR = auto()
    SE = auto()
    SENAO_SE = auto()
    SENAO = auto()
    ENQUANTO = auto()
    PARA = auto()
    EM = auto()
    INTERROMPER = auto()
    CONTINUAR = auto()
    IMPORTAR = auto()
    DE = auto()
    COMO = auto()
    LAMBDA = auto()
    CLASSE = auto()
    TENTE = auto()
    EXCETO = auto()
    FINALMENTE = auto()
    
    # Operadores
    MAIS = auto()
    MENOS = auto()
    MULTIPLICAR = auto()
    DIVIDIR = auto()
    DIVISAO_INTEIRA = auto()
    MODULO = auto()
    POTENCIA = auto()
    
    # Comparadores
    IGUAL = auto()
    DIFERENTE = auto()
    MAIOR = auto()
    MENOR = auto()
    MAIOR_IGUAL = auto()
    MENOR_IGUAL = auto()
    
    # Lógicos
    E = auto()
    OU = auto()
    NAO = auto()
    
    # Atribuição
    ATRIBUIR = auto()
    MAIS_ATRIBUIR = auto()
    MENOS_ATRIBUIR = auto()
    MULTIPLICAR_ATRIBUIR = auto()
    DIVIDIR_ATRIBUIR = auto()
    
    # Delimitadores
    PAREN_ESQUERDA = auto()
    PAREN_DIREITA = auto()
    COLCHETE_ESQUERDA = auto()
    COLCHETE_DIREITA = auto()
    CHAVE_ESQUERDA = auto()
    CHAVE_DIREITA = auto()
    VIRGULA = auto()
    DOIS_PONTOS = auto()
    PONTO = auto()
    SETA = auto()  # ->
    ASTERISCO = auto()
    
    # Especiais
    QUEBRA_LINHA = auto()
    INDENTACAO = auto()
    DESINDENTACAO = auto()
    EOF = auto()
    
    # Tags
    DIAMANTE_INICIO = auto()
    DIAMANTE_FIM = auto()


@dataclass
class Token:
    tipo: TokenType
    valor: any
    linha: int
    coluna: int


class Lexer:
    """Tokenizador da linguagem Diamante"""
    
    PALAVRAS_CHAVE = {
        'funcao': TokenType.FUNCAO,
        'retornar': TokenType.RETORNAR,
        'se': TokenType.SE,
        'senao_se': TokenType.SENAO_SE,
        'senao': TokenType.SENAO,
        'enquanto': TokenType.ENQUANTO,
        'para': TokenType.PARA,
        'em': TokenType.EM,
        'interromper': TokenType.INTERROMPER,
        'continuar': TokenType.CONTINUAR,
        'importar': TokenType.IMPORTAR,
        'de': TokenType.DE,
        'como': TokenType.COMO,
        'lambda': TokenType.LAMBDA,
        'classe': TokenType.CLASSE,
        'verdadeiro': TokenType.VERDADEIRO,
        'falso': TokenType.FALSO,
        'nulo': TokenType.NULO,
        'e': TokenType.E,
        'ou': TokenType.OU,
        'nao': TokenType.NAO,
        'tente': TokenType.TENTE,
        'exceto': TokenType.EXCETO,
        'finalmente': TokenType.FINALMENTE,
    }
    
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens: List[Token] = []
    
    def tokenizar(self) -> List[Token]:
        """Tokeniza o código completo"""
        while self.posicao < len(self.codigo):
            self._pular_espacos()
            
            if self.posicao >= len(self.codigo):
                break
            
            char_atual = self.codigo[self.posicao]
            
            # Comentários
            if char_atual == '#':
                self._pular_comentario()
                continue
            
            # Strings
            if char_atual in ('"', "'"):
                self._ler_string()
                continue
            
            # Números
            if char_atual.isdigit():
                self._ler_numero()
                continue
            
            # Identificadores e palavras-chave
            if char_atual.isalpha() or char_atual == '_':
                self._ler_identificador()
                continue
            
            # Tags <diamante>
            if char_atual == '<':
                if self.codigo[self.posicao:self.posicao+9] == '<diamante>':
                    self.tokens.append(Token(TokenType.DIAMANTE_INICIO, '<diamante>', self.linha, self.coluna))
                    self.posicao += 9
                    self.coluna += 9
                    continue
            
            # Tags </diamante>
            if char_atual == '<':
                if self.codigo[self.posicao:self.posicao+10] == '</diamante>':
                    self.tokens.append(Token(TokenType.DIAMANTE_FIM, '</diamante>', self.linha, self.coluna))
                    self.posicao += 10
                    self.coluna += 10
                    continue
            
            # Operadores e delimitadores
            if self._processar_operador():
                continue
            
            # Quebra de linha
            if char_atual == '\n':
                self.tokens.append(Token(TokenType.QUEBRA_LINHA, '\n', self.linha, self.coluna))
                self.posicao += 1
                self.linha += 1
                self.coluna = 1
                continue
            
            # Caractere desconhecido
            self.posicao += 1
            self.coluna += 1
        
        self.tokens.append(Token(TokenType.EOF, None, self.linha, self.coluna))
        return self.tokens
    
    def _pular_espacos(self):
        """Pula espaços em branco (não quebra de linha)"""
        while self.posicao < len(self.codigo) and self.codigo[self.posicao] in (' ', '\t'):
            self.posicao += 1
            self.coluna += 1
    
    def _pular_comentario(self):
        """Pula comentário de linha única"""
        while self.posicao < len(self.codigo) and self.codigo[self.posicao] != '\n':
            self.posicao += 1
            self.coluna += 1
    
    def _ler_string(self):
        """Lê uma string"""
        delimitador = self.codigo[self.posicao]
        inicio_coluna = self.coluna
        self.posicao += 1
        self.coluna += 1
        valor = ""
        
        while self.posicao < len(self.codigo) and self.codigo[self.posicao] != delimitador:
            if self.codigo[self.posicao] == '\\':
                self.posicao += 1
                self.coluna += 1
                if self.posicao < len(self.codigo):
                    # Escape simples
                    valor += self.codigo[self.posicao]
                    self.posicao += 1
                    self.coluna += 1
            else:
                valor += self.codigo[self.posicao]
                self.posicao += 1
                self.coluna += 1
        
        if self.posicao < len(self.codigo):
            self.posicao += 1  # Fecha a string
            self.coluna += 1
        
        self.tokens.append(Token(TokenType.STRING, valor, self.linha, inicio_coluna))
    
    def _ler_numero(self):
        """Lê um número"""
        inicio_coluna = self.coluna
        valor = ""
        
        while self.posicao < len(self.codigo) and (self.codigo[self.posicao].isdigit() or self.codigo[self.posicao] == '.'):
            valor += self.codigo[self.posicao]
            self.posicao += 1
            self.coluna += 1
        
        if '.' in valor:
            numero = float(valor)
        else:
            numero = int(valor)
        
        self.tokens.append(Token(TokenType.NUMERO, numero, self.linha, inicio_coluna))
    
    def _ler_identificador(self):
        """Lê um identificador ou palavra-chave"""
        inicio_coluna = self.coluna
        valor = ""
        
        while self.posicao < len(self.codigo) and (self.codigo[self.posicao].isalnum() or self.codigo[self.posicao] == '_'):
            valor += self.codigo[self.posicao]
            self.posicao += 1
            self.coluna += 1
        
        # Verifica se é uma palavra-chave
        tipo_token = self.PALAVRAS_CHAVE.get(valor, TokenType.IDENTIFICADOR)
        self.tokens.append(Token(tipo_token, valor, self.linha, inicio_coluna))
    
    def _processar_operador(self) -> bool:
        """Processa operadores e delimitadores"""
        char = self.codigo[self.posicao]
        prox_char = self.codigo[self.posicao + 1] if self.posicao + 1 < len(self.codigo) else None
        
        # Operadores de dois caracteres
        dois_chars = char + (prox_char or '')
        
        mapeamento_dois_chars = {
            '==': TokenType.IGUAL,
            '!=': TokenType.DIFERENTE,
            '>=': TokenType.MAIOR_IGUAL,
            '<=': TokenType.MENOR_IGUAL,
            '//': TokenType.DIVISAO_INTEIRA,
            '**': TokenType.POTENCIA,
            '+=': TokenType.MAIS_ATRIBUIR,
            '-=': TokenType.MENOS_ATRIBUIR,
            '*=': TokenType.MULTIPLICAR_ATRIBUIR,
            '/=': TokenType.DIVIDIR_ATRIBUIR,
            '->': TokenType.SETA,
        }
        
        if dois_chars in mapeamento_dois_chars:
            self.tokens.append(Token(mapeamento_dois_chars[dois_chars], dois_chars, self.linha, self.coluna))
            self.posicao += 2
            self.coluna += 2
            return True
        
        # Operadores de um caractere
        mapeamento_um_char = {
            '+': TokenType.MAIS,
            '-': TokenType.MENOS,
            '*': TokenType.MULTIPLICAR,
            '/': TokenType.DIVIDIR,
            '%': TokenType.MODULO,
            '=': TokenType.ATRIBUIR,
            '>': TokenType.MAIOR,
            '<': TokenType.MENOR,
            '(': TokenType.PAREN_ESQUERDA,
            ')': TokenType.PAREN_DIREITA,
            '[': TokenType.COLCHETE_ESQUERDA,
            ']': TokenType.COLCHETE_DIREITA,
            '{': TokenType.CHAVE_ESQUERDA,
            '}': TokenType.CHAVE_DIREITA,
            ',': TokenType.VIRGULA,
            ':': TokenType.DOIS_PONTOS,
            '.': TokenType.PONTO,
        }
        
        if char in mapeamento_um_char:
            self.tokens.append(Token(mapeamento_um_char[char], char, self.linha, self.coluna))
            self.posicao += 1
            self.coluna += 1
            return True
        
        return False
