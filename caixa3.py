from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from openpyxl import Workbook, load_workbook
from datetime import datetime
import json
import os

class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

class CaixaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.produtos = []
        self.carrinho = []
        self.vendas = []
        self.historico_grid = None  # Inicializa como None
        self.carregar_produtos()
        self.carregar_vendas()

    def build(self):
        self.tabs = TabbedPanel()

        cadastro_tab = TabbedPanelItem(text='Cadastro')
        cadastro_tab.content = self.criar_aba_cadastro()
        self.tabs.add_widget(cadastro_tab)

        vendas_tab = TabbedPanelItem(text='Vendas')
        vendas_tab.content = self.criar_aba_vendas()
        self.tabs.add_widget(vendas_tab)

        historico_tab = TabbedPanelItem(text='Histórico')
        historico_tab.content = self.criar_aba_historico()
        self.tabs.add_widget(historico_tab)

        relatorio_tab = TabbedPanelItem(text='Relatório')
        relatorio_tab.content = self.criar_aba_relatorio()
        self.tabs.add_widget(relatorio_tab)

        return self.tabs

    def criar_aba_cadastro(self):
        layout = BoxLayout(orientation='vertical')

        self.nome_input = TextInput(hint_text='Nome do Produto')
        self.preco_input = TextInput(hint_text='Preço')
        cadastrar_btn = Button(text='Cadastrar Produto', on_press=self.cadastrar_produto)

        self.produtos_cadastrados = GridLayout(cols=1, size_hint_y=None)
        self.produtos_cadastrados.bind(minimum_height=self.produtos_cadastrados.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(self.produtos_cadastrados)

        layout.add_widget(self.nome_input)
        layout.add_widget(self.preco_input)
        layout.add_widget(cadastrar_btn)
        layout.add_widget(scroll)

        self.atualizar_lista_produtos()

        return layout

    def criar_aba_vendas(self):
        layout = BoxLayout(orientation='vertical')

        self.produtos_grid = GridLayout(cols=3, size_hint_y=None)
        self.produtos_grid.bind(minimum_height=self.produtos_grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.5))
        scroll.add_widget(self.produtos_grid)

        self.total_label = Label(text='Total: R$ 0.00')
        self.forma_pagamento = Spinner(text='Forma de Pagamento', values=('Dinheiro', 'Cartão', 'PIX'))
        self.pagamento_input = TextInput(hint_text='Valor Recebido (se Dinheiro)')
        finalizar_btn = Button(text='Finalizar Venda', on_press=self.confirmar_venda)
        cancelar_btn = Button(text='Cancelar Venda', on_press=self.cancelar_venda)

        layout.add_widget(scroll)
        layout.add_widget(self.total_label)
        layout.add_widget(self.forma_pagamento)
        layout.add_widget(self.pagamento_input)
        layout.add_widget(finalizar_btn)
        layout.add_widget(cancelar_btn)

        self.atualizar_lista_produtos_venda()

        return layout

    def criar_aba_historico(self):
        layout = BoxLayout(orientation='vertical')

        self.historico_grid = GridLayout(cols=1, size_hint_y=None)  # Inicializa historico_grid
        self.historico_grid.bind(minimum_height=self.historico_grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.historico_grid)

        layout.add_widget(scroll)

        self.atualizar_historico()

        return layout

    def cadastrar_produto(self, instance):
        nome = self.nome_input.text
        preco = float(self.preco_input.text)
        produto = Produto(nome, preco)
        self.produtos.append(produto)
        self.salvar_produtos()

        self.nome_input.text = ''
        self.preco_input.text = ''

        self.atualizar_lista_produtos()
        self.atualizar_lista_produtos_venda()

    def excluir_produto(self, produto):
        self.produtos.remove(produto)
        self.salvar_produtos()
        self.atualizar_lista_produtos()
        self.atualizar_lista_produtos_venda()

    def atualizar_lista_produtos(self):
        self.produtos_cadastrados.clear_widgets()
        for produto in self.produtos:
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
            item.add_widget(Label(text=f"{produto.nome} - R$ {produto.preco:.2f}"))
            excluir_btn = Button(text='Excluir', size_hint_x=None, width=100)
            excluir_btn.bind(on_press=lambda x, p=produto: self.excluir_produto(p))
            item.add_widget(excluir_btn)
            self.produtos_cadastrados.add_widget(item)

    def atualizar_lista_produtos_venda(self):
        self.produtos_grid.clear_widgets()
        for produto in self.produtos:
            btn = Button(text=f"{produto.nome}\nR$ {produto.preco:.2f}", size_hint_y=None, height=44)
            btn.bind(on_press=self.adicionar_ao_carrinho)
            self.produtos_grid.add_widget(btn)

    def adicionar_ao_carrinho(self, instance):
        produto = next(p for p in self.produtos if p.nome in instance.text)
        self.carrinho.append(produto)
        self.atualizar_total()

    def atualizar_total(self):
        total = sum(produto.preco for produto in self.carrinho)
        self.total_label.text = f'Total: R$ {total:.2f}'

    def confirmar_venda(self, instance):
        if not self.carrinho:
            self.mostrar_popup("Erro", "O carrinho está vazio!")
            return

        resumo = "Resumo da Compra:\n\n"
        for produto in self.carrinho:
            resumo += f"{produto.nome}: R$ {produto.preco:.2f}\n"

        total = sum(produto.preco for produto in self.carrinho)
        resumo += f"\nTotal: R$ {total:.2f}"
        resumo += f"\nForma de Pagamento: {self.forma_pagamento.text}"

        if self.forma_pagamento.text == 'Dinheiro':
            try:
                valor_recebido = float(self.pagamento_input.text)
                troco = valor_recebido - total
                if troco < 0:
                    self.mostrar_popup("Erro", "Valor recebido insuficiente!")
                    return
                resumo += f"\nValor Recebido: R$ {valor_recebido:.2f}"
                resumo += f"\nTroco: R$ {troco:.2f}"
            except ValueError:
                self.mostrar_popup("Erro", "Por favor, insira um valor válido para o pagamento em dinheiro.")
                return

        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=resumo))

        botoes = BoxLayout()
        confirmar_btn = Button(text='Confirmar', on_press=self.finalizar_venda)
        cancelar_btn = Button(text='Cancelar')

        botoes.add_widget(confirmar_btn)
        botoes.add_widget(cancelar_btn)
        content.add_widget(botoes)

        popup = Popup(title='Confirmar Venda', content=content, size_hint=(0.9, 0.9))
        cancelar_btn.bind(on_press=popup.dismiss)
        popup.open()

    def finalizar_venda(self, instance):
        total = sum(produto.preco for produto in self.carrinho)
        venda = {
            'data': datetime.now().strftime("%d-%m-%y %H:%M:%S"),
            'produtos': [{'nome': p.nome, 'preco': p.preco} for p in self.carrinho],
            'total': total,
            'forma_pagamento': self.forma_pagamento.text
        }
        self.vendas.append(venda)
        self.salvar_vendas()

        if self.forma_pagamento.text == 'Dinheiro':
            valor_recebido = float(self.pagamento_input.text)
            troco = valor_recebido - total
            self.mostrar_popup("Venda Finalizada", f"Venda finalizada com sucesso!\nTroco: R$ {troco:.2f}")
        else:
            self.mostrar_popup("Venda Finalizada", "Venda finalizada com sucesso!")

        self.carrinho.clear()
        self.atualizar_total()
        self.pagamento_input.text = ''
        self.forma_pagamento.text = 'Forma de Pagamento'
        self.atualizar_historico()

    def cancelar_venda(self, instance):
        self.carrinho.clear()
        self.atualizar_total()
        self.pagamento_input.text = ''
        self.forma_pagamento.text = 'Forma de Pagamento'
        self.mostrar_popup("Venda Cancelada", "A venda foi cancelada.")

    def atualizar_historico(self):
        if not hasattr(self, 'historico_grid') or self.historico_grid is None:
            return  # Impede que o erro ocorra se a aba ainda não foi inicializada

        self.historico_grid.clear_widgets()
        for i, venda in enumerate(self.vendas):
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
            item.add_widget(Label(text=f"Data: {venda['data']}"))
            
            # Adiciona os itens comprados
            itens_text = "\n\nItens comprados:\n"
            for produto in venda['produtos']:
                itens_text += f"- {produto['nome']}: R$ {produto['preco']:.2f}\n"
            item.add_widget(Label(text=itens_text))
            
            item.add_widget(Label(text=f"\n\nTotal: R$ {venda['total']:.2f}"))
            item.add_widget(Label(text=f"\nForma de Pagamento: {venda['forma_pagamento']}"))
            excluir_btn = Button(text='Excluir Venda', size_hint_y=None, height=30)
            excluir_btn.bind(on_press=lambda x, index=i: self.excluir_venda(index))
            item.add_widget(excluir_btn)
            self.historico_grid.add_widget(item)

    def excluir_venda(self, index):
        del self.vendas[index]
        self.salvar_vendas()
        self.atualizar_historico()

    def mostrar_popup(self, titulo, mensagem):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=mensagem))
        fechar_btn = Button(text='Fechar', size_hint_y=None, height=44)
        content.add_widget(fechar_btn)

        popup = Popup(title=titulo, content=content, size_hint=(0.8, 0.5))
        fechar_btn.bind(on_press=popup.dismiss)
        popup.open()

    def salvar_produtos(self):
        with open('produtos.json', 'w') as f:
            json.dump([{'nome': p.nome, 'preco': p.preco} for p in self.produtos], f)

    def carregar_produtos(self):
        if os.path.exists('produtos.json'):
            with open('produtos.json', 'r') as f:
                produtos_data = json.load(f)
                self.produtos = [Produto(p['nome'], p['preco']) for p in produtos_data]

    def salvar_vendas(self):
        with open('vendas.json', 'w') as f:
            json.dump(self.vendas, f)

    def carregar_vendas(self):
        if os.path.exists('vendas.json'):
            with open('vendas.json', 'r') as f:
                self.vendas = json.load(f)

    def criar_aba_relatorio(self):
        layout = BoxLayout(orientation='vertical')

        self.relatorio_grid = GridLayout(cols=1, size_hint_y=None)
        self.relatorio_grid.bind(minimum_height=self.relatorio_grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.relatorio_grid)

        layout.add_widget(scroll)

        self.atualizar_relatorio()

        return layout            

    def atualizar_relatorio(self):
        # Limpar a tabela de relatórios
        self.relatorio_grid.clear_widgets()

        # Dicionário para contar as vendas de cada produto
        produto_vendas = {}
        total_vendas = 0

        for venda in self.vendas:
            total_vendas += venda['total']
            for produto in venda['produtos']:
                nome_produto = produto['nome']
                preco_produto = produto['preco']

                if nome_produto not in produto_vendas:
                    produto_vendas[nome_produto] = {'quantidade': 0, 'total': 0.0}

                produto_vendas[nome_produto]['quantidade'] += 1
                produto_vendas[nome_produto]['total'] += preco_produto

        # Adicionar as informações no layout do relatório
        for nome_produto, dados in produto_vendas.items():
            quantidade = dados['quantidade']
            total = dados['total']
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
            item.add_widget(Label(text=f"{nome_produto}"))
            item.add_widget(Label(text=f"Quantidade Vendida: {quantidade}"))
            item.add_widget(Label(text=f"Total Vendido: R$ {total:.2f}"))
            self.relatorio_grid.add_widget(item)

        # Adicionar o valor total de todas as vendas
        total_label = Label(text=f"Valor Total de Todas as Vendas: R$ {total_vendas:.2f}", size_hint_y=None, height=44)
        self.relatorio_grid.add_widget(total_label)

if __name__ == '__main__':
    CaixaApp().run()
