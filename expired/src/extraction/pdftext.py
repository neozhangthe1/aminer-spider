# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 10:18:19 2011

@author: jayronsoares
"""
from elixir import *
import os,subprocess
import glob
import codecs

metadata.bind = "mysql://root:password@localhost/Artigos"
metadata.bind.echo = False


# Criando classe para tabela do banco de dados
class Artigo(Entity):
    using_options(tablename='artigo')
    arquivo = Field(Unicode(128))
    texto = Field(UnicodeText)
    

def Cria_Tabela():
    setup_all()
    create_all()
    

lista_pdf = glob.glob('/home/jayron/Documentos/Bayes/*.pdf')
#print lista_pdf

# Criando a função para converte pdfs
def Converte_PDF(lista_pdf):
    """
    Executa a chamada do aplicativo PDF_TO_TEXT, o qual transforma
    um dado arquivo pdf para texto, e posteriormente envia para 
    a base de dados do Solr.
    """
    
    # Criando uma lista vazia para receber os pdfs
    lista = []
    
    # Fazendo a iteração na lista_pdf
    for n,pdf in enumerate(lista_pdf):
        
        # Executando a chamada do aplicativo PDFTOTEXT
        print pdf
        p = subprocess.Popen('pdftotext %s'%pdf, shell=True)
        sts = os.waitpid(p.pid, 0)[1]
        
        
        if sts == 0:
            
            # variável que recebe o arquivo em formato .txt         
            nome_txt = pdf.replace('.pdf','.txt')
            
            # Abrindo o arquivo/variável nome_txt        
            
            with open(nome_txt,'r') as arq: 
            
                # Variável para receber a leitura da variável nome_text              
                
                texto = arq.read()
                
            # Adiciona um dicionário à lista, antes vazia.   
            lista.append({'arquivo':pdf, 'texto':texto})
            
            # Remove do diretório do sistema, os arquivos transformados em texto.
            os.remove(nome_txt)
        else:
            print "Conversao do arquivo %s falhou"%pdf

    return lista

def Salva_PDF(lista):
    for i in lista:
        print i.keys()
        a = Artigo(**i)
    session.commit()
        
    
if __name__ == "__main__":
    
    Cria_Tabela()
    lis = Converte_PDF(lista_pdf)
    
    # Alteração
    Salva_PDF(lis)
