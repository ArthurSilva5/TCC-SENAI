import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------------------------------------------------------------------------------
# Criando a conexão com  o Banco de Dados
bd = mysql.connector.connect (
    host= "b0cbbo0hah9hwzfrwlai-mysql.services.clever-cloud.com",
    user= "udpbunqavprea99n",
    password= "9ylNhu6Mlk5U6ODiczNv",
    port= "3306",
    database= "b0cbbo0hah9hwzfrwlai"
)

# Criando o Cursor
cursor = bd.cursor(buffered=True)

# ----------------------------------------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------------------------------------
# Criando o layout
st.sidebar.title('Menu de Opções')
esc = st.sidebar.selectbox('Selecione sua opção:',['Página Inicial','Adicionar Despesa','Adicionar Recebimento','Relatório de Gastos','Gráfico de Gastos','Remover Despesas','Remover Recebimentos'])


# Criando a Página Inicial
if esc == 'Página Inicial':
    st.title('Bem-Vindo(a) ao CashCount, o software que organiza suas despesas!')
    st.balloons()
    st.header('Este software foi desenvolvido com a finalidade de auxiliar você a controlar melhor seu dinheiro, visando a percepção de gastos desenecessários!')
    st.header("Confira nossas funcionalidades clicando na seta no canto superior esquerdo!")
#------------------------------------------------------------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------------------------------------------------------------
# Criando a Página de adicionar despesas
def despesas():
    if esc == 'Adicionar Despesa':
        st.title('Controlador de Despesas')
        st.subheader("Registre sua depesa abaixo:")
        produto   =  st.text_input('Nome da depesa:')
        produto.strip()
        valor     =  st.number_input('Valor do despesa:', min_value=0.01)
        data      =  st.date_input('Data de Compra:', )
        categoria =  st.selectbox("Escolha a categoria da despesa:",("Alimentação","Vestuário","Transporte","Lazer","Contas Mensais","Outra categoria"))
        btn       =  st.button('Confirmar')

        # Formatando o valor, retirandos virgulas desnecessárias
        valor = str(valor)
        valor = valor.replace(",","")
        valor = float(valor)
        valor = f"{valor:.2f}"

        # Adicionando os dados para o Banco de dados
        
        if btn == True:
            if not(produto and produto.strip()):
                st.error("Erro! Você não preencheu todos os campos necessários!")
            else:
                sql = ("INSERT INTO despesas (produto,valor,datas,categoria) VALUES (%s,%s,%s,%s)")
                val = (produto,valor,data,categoria)
                cursor.execute(sql,val)
                bd.commit()
                st.success("Registro salvo com sucesso!")


despesas()
#------------------------------------------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------------------------------------------
# Criando a Página de Adicionar Recebimento:
def recebimento():
    if esc == 'Adicionar Recebimento':
        st.subheader('Adicionar recebimento') 
        valor     = st.number_input('Valor Recebido:', min_value= 0.01)
        data      = st.date_input('Data de Recebimento:')
        categoria = st.selectbox("Escolha a categoria de recebimento:",("Salário","Outros recebimentos"))
        btn       = st.button('Confirmar')


        # Adicionando os dados para o Banco de dados
        if btn == True:
            sql = ("INSERT INTO recibos (valor,datas,categoria) VALUES (%s,%s,%s)")
            val = (valor,data,categoria)
            cursor.execute(sql,val)
            bd.commit()
            st.success("Registro salvo com sucesso!")
recebimento()

#------------------------------------------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------------------------------------------
# Criando a Página do relatório de gastos:
def relatorio():
    if esc == 'Relatório de Gastos':
        st.title('Confira um relatório de suas despesas e recibos: ')
        st.header("Escolha entre quais períodos de datas você deseja vizualizar dados:")

        data_inicial = st.date_input("Selecione a data inicial")
        data_final = st.date_input("Selecione a data final")
        

        # Criando a tabela
        tabela = cursor.execute(f"SELECT produto,valor,datas,categoria FROM despesas WHERE datas BETWEEN '{data_inicial}' AND '{data_final}'") # Pega os itens do banco 
        tabela = cursor.fetchall()  # Cria a tabela com linhas
        df = pd.DataFrame(tabela,  columns = ["Produto","Valor","Data","Categoria"])
        df['Valor'] = df['Valor'].map(lambda x: '%.2f' % x)  # Comando usado para formatar os valores em dinheiro
        # st.table(df) -> Vai ser imprimida no final
    #---------------------------------------------------------------------------------------------------------------


    #---------------------------------------------------------------------------------------------------------------
        # Criando a soma de despesas
        lista_de_depesas = df['Valor'].to_list()                    # Cria a lista com os valores da coluna Valor
        valores_depesas = [float(val) for val in lista_de_depesas]  # Transforma os valores em float
        saldo = sum(valores_depesas)                                # Soma os valores
        st.subheader(f"Total de despesas: R${saldo:.2f}")           # Cria o total de despesas       
    #---------------------------------------------------------------------------------------------------------------


    #---------------------------------------------------------------------------------------------------------------
    # Imprimindo a tabela de recebimentos:

        tabela = cursor.execute(f"SELECT valor,categoria,datas FROM recibos WHERE datas BETWEEN '{data_inicial}' AND '{data_final}'")
        tabela = cursor.fetchall()
        dfr = pd.DataFrame(tabela, columns = ["Valor","Data","Categoria"])
        dfr['Valor'] = dfr['Valor'].map(lambda x: '%.2f' % x)    # Comando usado para formatar os valores em dinheiro
        #st.table(dfr)  -> Vai ser imprimida no final
    #--------------------------------------------------------------------------------------------------------------   


    #--------------------------------------------------------------------------------------------------------------
        # Criando o saldo atual:
        lista = dfr['Valor'].to_list()                  # Cria uma lista com os valores da coluna da Valor
        valores_depesas = [float(val) for val in lista] # Transforma os itens da lista no tipo float 
        saldo_recebido = sum(valores_depesas)           # Soma os valores
        saldofinal = saldo_recebido-saldo               # Cria o Saldo final

        if saldofinal > 0:
            st.subheader(f"Saldo: R${saldofinal:.2f}")
        else:
            saldofinal = abs(saldofinal)
            st.subheader(f"Saldo: -R${saldofinal:.2f}")


        # Imprimindo a tabela de despesas:
        coluna = ['Valor']
        st.header('Despesas:')
        st.dataframe(df.style.set_properties(**{'background-color': '#F17474'}, subset= coluna)) 
        # imprimindo a tabela e colorindo os valores da coluna Valor

        #--------------------------------
        # Imprimindo a tabela de entradas:
        st.header("Entradas:")
        st.dataframe(dfr.style.set_properties(**{'background-color': '#54F176'}, subset= coluna))
relatorio()
#--------------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------------------------------------------
# Criando a Página do gráfico de gastos:
def graficos():
    if esc == "Gráfico de Gastos":

        st.header("Escolha o período que deseja vizualizar gráficos e informações:")
        data_inicial = st.date_input("Digite a data inicial")
        data_final = st.date_input("Digite a data final")

        # Criando a tabela
        tabela = cursor.execute(f"SELECT produto,valor,datas,categoria FROM despesas WHERE datas BETWEEN '{data_inicial}' AND '{data_final}'") # Pega os itens do banco 
        tabela = cursor.fetchall()  # Cria a tabela com linhas
        df = pd.DataFrame(tabela,  columns = ["Produto","Valor","Data","Categoria"])
        df['Valor'] = df['Valor'].map(lambda x: '%.2f' % x)  # Comando usado para formatar os valores em dinheiro
        

        # Pegando os valores totais de cada categoria de despesa
        df['Valor'] = df['Valor'].astype(float)
        valores = df.groupby(['Categoria'], as_index=False).sum()
    #   st.write(valores)

        # Novo dataframe com Categoria e valor
        novo_df = pd.DataFrame(valores, columns = ['Categoria','Valor'])
        novo_df['Valor'] = novo_df['Valor'].map(lambda x: '%.2f' % x) # Formatação de valores
        st.header("Tabela de gastos por categoria")
        st.dataframe(novo_df)

        # Rótulos
        categorias = novo_df['Categoria'].to_list()
        valores = novo_df['Valor'].to_list()
        cores = ['darkgreen','gold','red','PaleVioletRed','Purple','darkblue']

        st.header("Escolha o estilo de gráfico que deseja vizualizar")
        escolha = st.selectbox(" ",
                            ('Gráfico de Pizza','Gráfico de Barras'))

        if escolha == 'Gráfico de Pizza':
            # Gráfico de pizza
            plt.pie(valores, labels = categorias,  autopct='%1.1f%%', colors = cores)
            plt.title("Gráfico de Pizza com os gastos por categoria de despesa:")
            st.pyplot(plt)

        elif escolha == 'Gráfico de Barras':
            lista_de_valores = novo_df['Valor'].to_list()    
            valores = [float(val) for val in lista_de_valores]
            plt.barh(categorias,valores, color = 'RoyalBlue')
            plt.title("Gráfico de Barras Horizontal")
            plt.xlabel("Valor Gasto por categoria (R$)")
            plt.ylabel("Categorias")
            st.pyplot(plt)
graficos()


def remover():
    if esc == "Remover Despesas":

        st.header("Escolha o período que deseja vizualizar informações:")
        data_inicial = st.date_input("Digite a data inicial")
        data_final = st.date_input("Digite a data final")

        # Criando a tabela
        tabela = cursor.execute(f"SELECT id,produto,valor,datas,categoria FROM despesas WHERE datas BETWEEN '{data_inicial}' AND '{data_final}'") # Pega os itens do banco 
        tabela = cursor.fetchall()  # Cria a tabela com linhas
        df = pd.DataFrame(tabela,  columns = ["ID","Produto","Valor","Data","Categoria"])
        df['Valor'] = df['Valor'].map(lambda x: '%.2f' % x)  # Comando usado para formatar os valores em dinheiro
#        st.dataframe(df2)

        _funct = st.sidebar.radio(label="Funções", options = ['Remover'])

        st.header("Tabela de Despesas")
        st.subheader("Selecione os itens que deseja excluir")

        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True,groupable=True)

        if _funct == 'Remover':
            sel_mode = st.radio('Tipo de seleção', options = ['multiple'])
            gd.configure_selection(selection_mode=sel_mode,use_checkbox=True)
            gridoptions = gd.build()

            grid_table = AgGrid(df,gridOptions=gridoptions,  
                        update_mode= GridUpdateMode.SELECTION_CHANGED,
                        height = 400,
                        allow_unsafe_jscode=True,
                        #enable_enterprise_modules = True,
                        theme = 'fresh')
                        
            sel_row = grid_table['selected_rows'] # Seleciona as linhas escolhidas pelos usuários

            btn = st.button('EXCLUIR') # Cria o botão
            if btn == True:
                for item in sel_row:
                    indice = item["ID"]
                    cursor.execute(f"DELETE FROM despesas WHERE id = {indice}")
                    bd.commit()
                st.warning("Os dados foram excluidos! Atualize a página para visualizar atualizações!")
remover()
#------------------------------------------------------------------------------------------------------------------------------------------
def removerRecibo():
    if esc == "Remover Recebimentos":

        st.header("Escolha o período que deseja vizualizar informações:")
        data_inicial = st.date_input("Digite a data inicial")
        data_final = st.date_input("Digite a data final")

        # Criando a tabela
        tabela = cursor.execute(f"SELECT id,valor,datas,categoria FROM recibos WHERE datas BETWEEN '{data_inicial}' AND '{data_final}'") # Pega os itens do banco 
        tabela = cursor.fetchall()  # Cria a tabela com linhas
        df = pd.DataFrame(tabela,  columns = ["ID","Valor","Data","Categoria"])
        df['Valor'] = df['Valor'].map(lambda x: '%.2f' % x)  # Comando usado para formatar os valores em dinheiro
#        st.dataframe(df2)

        _funct = st.sidebar.radio(label="Funções", options = ['Remover'])

        st.header("Tabela de Recebimentos")
        st.subheader("Selecione os itens que deseja excluir")

        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True,groupable=True)

        if _funct == 'Remover':
            sel_mode = st.radio('Tipo de seleção', options = ['multiple'])
            gd.configure_selection(selection_mode=sel_mode,use_checkbox=True)
            gridoptions = gd.build()

            grid_table = AgGrid(df,gridOptions=gridoptions,  
                        update_mode= GridUpdateMode.SELECTION_CHANGED,
                        height = 400,
                        allow_unsafe_jscode=True,
                        #enable_enterprise_modules = True,
                        theme = 'fresh')
                        
            sel_row = grid_table['selected_rows'] # Seleciona as linhas escolhidas pelos usuários

            btn = st.button('EXCLUIR') # Cria o botão
            if btn == True:
                for item in sel_row:
                    indice = item["ID"]
                    cursor.execute(f"DELETE FROM recibos WHERE id = {indice}")
                    bd.commit()
                st.warning("Os dados foram excluidos! Atualize a página para visualizar atualizações!")
removerRecibo()