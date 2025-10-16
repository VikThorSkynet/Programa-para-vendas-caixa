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
from kivy.graphics import Color, Rectangle, Line
from openpyxl import Workbook, load_workbook
from datetime import datetime
import json
import os

class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.86, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '16sp'

class DangerButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.9, 0.3, 0.3, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '16sp'

class SuccessButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.7, 0.3, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '16sp'

class WarningButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.95, 0.6, 0.1, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '16sp'

class SmallDangerButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.9, 0.3, 0.3, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '14sp'

class StyledLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.2, 0.2, 0.2, 1)
        self.font_size = '14sp'

class TitleLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.1, 0.1, 0.1, 1)
        self.font_size = '20sp'
        self.bold = True
        self.size_hint_y = None
        self.height = 50

class SectionLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.1, 0.1, 0.1, 1)
        self.font_size = '18sp'
        self.bold = True
        self.size_hint_y = None
        self.height = 40

class CaixaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.produtos = []
        self.carrinho = []
        self.vendas = []
        self.historico_grid = None
        self.carregar_produtos()
        self.carregar_vendas()

    def build(self):
        self.tabs = TabbedPanel(do_default_tab=False)
        self.tabs.background_color = (0.95, 0.95, 0.95, 1)
        self.tabs.tab_width = 150

        # Aba de Vendas como primeira (mais usada)
        vendas_tab = TabbedPanelItem(text='VENDAS')
        vendas_tab.content = self.criar_aba_vendas()
        self.tabs.add_widget(vendas_tab)

        cadastro_tab = TabbedPanelItem(text='PRODUTOS')
        cadastro_tab.content = self.criar_aba_cadastro()
        self.tabs.add_widget(cadastro_tab)

        historico_tab = TabbedPanelItem(text='HISTORICO')
        historico_tab.content = self.criar_aba_historico()
        self.tabs.add_widget(historico_tab)

        relatorio_tab = TabbedPanelItem(text='RELATORIO')
        relatorio_tab.content = self.criar_aba_relatorio()
        self.tabs.add_widget(relatorio_tab)

        return self.tabs

    def criar_aba_cadastro(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(TitleLabel(text='Gerenciar Produtos'))

        # Conteudo principal com scroll
        main_content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        main_content.bind(minimum_height=main_content.setter('height'))

        # Formulario de cadastro
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=200)
        
        self.nome_input = TextInput(
            hint_text='Digite o nome do produto...',
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50
        )
        
        self.preco_input = TextInput(
            hint_text='Digite o preco (ex: 10,50)',
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50
        )
        
        cadastrar_btn = SuccessButton(
            text='CADASTRAR PRODUTO',
            size_hint_y=None,
            height=60,
            on_press=self.cadastrar_produto
        )

        form_layout.add_widget(self.nome_input)
        form_layout.add_widget(self.preco_input)
        form_layout.add_widget(cadastrar_btn)
        
        main_content.add_widget(form_layout)

        # Separador
        separator = Label(text='_' * 50, size_hint_y=None, height=30)
        main_content.add_widget(separator)

        # Lista de produtos
        self.produtos_label_cadastro = Label(
            text=f'Produtos Cadastrados ({len(self.produtos)})',
            size_hint_y=None,
            height=40,
            font_size='18sp',
            bold=True
        )
        main_content.add_widget(self.produtos_label_cadastro)

        self.produtos_cadastrados = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.produtos_cadastrados.bind(minimum_height=self.produtos_cadastrados.setter('height'))
        main_content.add_widget(self.produtos_cadastrados)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(main_content)
        layout.add_widget(scroll)

        self.atualizar_lista_produtos()

        return layout

    def criar_aba_vendas(self):
        # Layout principal horizontal (2 colunas)
        layout = BoxLayout(orientation='horizontal', padding=10, spacing=15)

        # ===== COLUNA ESQUERDA: CARDAPIO DE PRODUTOS =====
        coluna_produtos = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.55)
        
        coluna_produtos.add_widget(SectionLabel(text='CARDAPIO DE PRODUTOS'))

        # Campo de busca
        busca_layout = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=5)
        busca_layout.add_widget(Label(
            text='Buscar:',
            size_hint_x=None,
            width=80,
            font_size='16sp',
            bold=True
        ))
        
        self.busca_input = TextInput(
            hint_text='Digite o nome do produto...',
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50
        )
        self.busca_input.bind(text=self.filtrar_produtos_venda)
        
        limpar_busca_btn = StyledButton(
            text='LIMPAR',
            size_hint_x=None,
            width=100
        )
        limpar_busca_btn.bind(on_press=self.limpar_busca)
        
        busca_layout.add_widget(self.busca_input)
        busca_layout.add_widget(limpar_busca_btn)
        coluna_produtos.add_widget(busca_layout)

        # Grid de produtos com scroll
        self.produtos_grid = GridLayout(cols=2, size_hint_y=None, spacing=10, padding=5)
        self.produtos_grid.bind(minimum_height=self.produtos_grid.setter('height'))

        scroll_produtos = ScrollView(size_hint=(1, 1))
        scroll_produtos.add_widget(self.produtos_grid)
        coluna_produtos.add_widget(scroll_produtos)

        layout.add_widget(coluna_produtos)

        # ===== COLUNA DIREITA: CARRINHO E PAGAMENTO =====
        coluna_carrinho = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.45)
        
        coluna_carrinho.add_widget(SectionLabel(text='CARRINHO DE COMPRAS'))

        # Carrinho com scroll
        self.carrinho_grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.carrinho_grid.bind(minimum_height=self.carrinho_grid.setter('height'))

        scroll_carrinho = ScrollView(size_hint=(1, 0.45))
        scroll_carrinho.add_widget(self.carrinho_grid)
        coluna_carrinho.add_widget(scroll_carrinho)

        # Botao limpar carrinho
        limpar_carrinho_btn = DangerButton(
            text='LIMPAR CARRINHO',
            size_hint_y=None,
            height=50,
            on_press=self.limpar_carrinho_completo
        )
        coluna_carrinho.add_widget(limpar_carrinho_btn)

        # Total com destaque
        total_box = BoxLayout(size_hint_y=None, height=60, padding=10)
        self.total_label = Label(
            text='TOTAL: R$ 0.00',
            font_size='24sp',
            bold=True,
            color=(0.1, 0.5, 0.1, 1)
        )
        total_box.add_widget(self.total_label)
        coluna_carrinho.add_widget(total_box)

        # Separador
        coluna_carrinho.add_widget(Label(text='_' * 30, size_hint_y=None, height=20))

        # Forma de pagamento
        coluna_carrinho.add_widget(Label(
            text='Forma de Pagamento:',
            size_hint_y=None,
            height=30,
            font_size='14sp',
            bold=True
        ))
        
        self.forma_pagamento = Spinner(
            text='Selecione...',
            values=('Dinheiro', 'Cartao', 'PIX'),
            size_hint_y=None,
            height=50,
            font_size='16sp'
        )
        coluna_carrinho.add_widget(self.forma_pagamento)

        self.pagamento_input = TextInput(
            hint_text='Valor recebido (apenas para dinheiro)',
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50
        )
        coluna_carrinho.add_widget(self.pagamento_input)

        # Botoes de acao
        botoes_box = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        cancelar_btn = DangerButton(
            text='CANCELAR',
            on_press=self.cancelar_venda
        )
        
        finalizar_btn = SuccessButton(
            text='FINALIZAR VENDA',
            on_press=self.confirmar_venda
        )

        botoes_box.add_widget(cancelar_btn)
        botoes_box.add_widget(finalizar_btn)
        coluna_carrinho.add_widget(botoes_box)

        layout.add_widget(coluna_carrinho)

        self.atualizar_lista_produtos_venda()
        self.atualizar_visualizacao_carrinho()

        return layout

    def criar_aba_historico(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.historico_titulo = TitleLabel(text=f'Historico de Vendas ({len(self.vendas)})')
        layout.add_widget(self.historico_titulo)

        self.historico_grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.historico_grid.bind(minimum_height=self.historico_grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.historico_grid)
        layout.add_widget(scroll)

        self.atualizar_historico()

        return layout

    def criar_aba_relatorio(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(TitleLabel(text='Relatorio de Vendas'))

        self.relatorio_grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.relatorio_grid.bind(minimum_height=self.relatorio_grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.relatorio_grid)
        layout.add_widget(scroll)

        self.atualizar_relatorio()

        return layout

    def limpar_busca(self, instance):
        self.busca_input.text = ''
        self.filtrar_produtos_venda(None, '')

    def filtrar_produtos_venda(self, instance, value):
        texto_busca = value.lower().strip()
        self.produtos_grid.clear_widgets()
        
        produtos_filtrados = [p for p in self.produtos if texto_busca in p.nome.lower()]
        
        if not produtos_filtrados:
            self.produtos_grid.add_widget(
                Label(
                    text='Nenhum produto encontrado.',
                    size_hint_y=None,
                    height=100
                )
            )
            return
        
        for produto in produtos_filtrados:
            btn = StyledButton(
                text=f"{produto.nome}\n\nR$ {produto.preco:.2f}",
                size_hint_y=None,
                height=90
            )
            btn.bind(on_press=self.adicionar_ao_carrinho)
            self.produtos_grid.add_widget(btn)

    def cadastrar_produto(self, instance):
        nome = self.nome_input.text.strip()
        
        if not nome:
            self.mostrar_popup("Atencao", "Por favor, digite o nome do produto!")
            return
            
        try:
            preco_str = self.preco_input.text.replace(',', '.')
            preco = float(preco_str)
            if preco <= 0:
                self.mostrar_popup("Atencao", "O preco deve ser maior que zero!")
                return
        except ValueError:
            self.mostrar_popup("Atencao", "Por favor, insira um preco valido!")
            return

        produto = Produto(nome, preco)
        self.produtos.append(produto)
        self.salvar_produtos()

        self.nome_input.text = ''
        self.preco_input.text = ''

        self.atualizar_lista_produtos()
        self.atualizar_lista_produtos_venda()
        
        self.mostrar_popup("Sucesso", f"Produto '{nome}' cadastrado com sucesso!")

    def editar_produto(self, produto):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text=f'Editar Produto: {produto.nome}',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        ))
        
        nome_input = TextInput(
            text=produto.nome,
            hint_text='Nome do produto',
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50
        )
        
        preco_input = TextInput(
            text=str(produto.preco).replace('.', ','),
            hint_text='Preco',
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50
        )
        
        content.add_widget(nome_input)
        content.add_widget(preco_input)
        
        botoes = BoxLayout(size_hint_y=None, height=60, spacing=10)
        popup = Popup(title='Editar Produto', content=content, size_hint=(0.8, 0.5))
        
        salvar_btn = SuccessButton(text='SALVAR')
        salvar_btn.bind(on_press=lambda x: self.salvar_edicao_produto(produto, nome_input.text, preco_input.text, popup))
        
        cancelar_btn = DangerButton(text='CANCELAR')
        cancelar_btn.bind(on_press=popup.dismiss)
        
        botoes.add_widget(cancelar_btn)
        botoes.add_widget(salvar_btn)
        content.add_widget(botoes)
        
        popup.open()

    def salvar_edicao_produto(self, produto, novo_nome, novo_preco, popup):
        novo_nome = novo_nome.strip()
        
        if not novo_nome:
            self.mostrar_popup("Atencao", "O nome do produto nao pode estar vazio!")
            return
        
        try:
            preco_str = novo_preco.replace(',', '.')
            preco = float(preco_str)
            if preco <= 0:
                self.mostrar_popup("Atencao", "O preco deve ser maior que zero!")
                return
        except ValueError:
            self.mostrar_popup("Atencao", "Por favor, insira um preco valido!")
            return
        
        produto.nome = novo_nome
        produto.preco = preco
        
        self.salvar_produtos()
        self.atualizar_lista_produtos()
        self.atualizar_lista_produtos_venda()
        
        popup.dismiss()
        self.mostrar_popup("Sucesso", "Produto editado com sucesso!")

    def excluir_produto(self, produto):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f'Deseja realmente excluir o produto:\n\n"{produto.nome}"?',
            font_size='16sp'
        ))
        
        botoes = BoxLayout(size_hint_y=None, height=50, spacing=10)
        popup = Popup(title='Confirmar Exclusao', content=content, size_hint=(0.8, 0.4))
        
        confirmar_btn = DangerButton(text='SIM, EXCLUIR')
        confirmar_btn.bind(on_press=lambda x: self.confirmar_exclusao_produto(produto, popup))
        
        cancelar_btn = StyledButton(text='CANCELAR')
        cancelar_btn.bind(on_press=popup.dismiss)
        
        botoes.add_widget(cancelar_btn)
        botoes.add_widget(confirmar_btn)
        content.add_widget(botoes)
        
        popup.open()

    def confirmar_exclusao_produto(self, produto, popup):
        popup.dismiss()
        self.produtos.remove(produto)
        self.salvar_produtos()
        self.atualizar_lista_produtos()
        self.atualizar_lista_produtos_venda()
        self.mostrar_popup("Sucesso", "Produto excluido com sucesso!")

    def atualizar_lista_produtos(self):
        self.produtos_cadastrados.clear_widgets()
        
        # Atualizar contador
        if hasattr(self, 'produtos_label_cadastro'):
            self.produtos_label_cadastro.text = f'Produtos Cadastrados ({len(self.produtos)})'
        
        if not self.produtos:
            self.produtos_cadastrados.add_widget(
                Label(
                    text='Nenhum produto cadastrado.\nClique em "Cadastrar Produto" para adicionar.',
                    size_hint_y=None,
                    height=100,
                    font_size='14sp'
                )
            )
            return
        
        for produto in self.produtos:
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
            
            info_label = Label(
                text=f"  {produto.nome}",
                size_hint_x=0.4,
                font_size='16sp'
            )
            
            preco_label = Label(
                text=f"R$ {produto.preco:.2f}",
                size_hint_x=0.2,
                font_size='18sp',
                bold=True,
                color=(0.1, 0.5, 0.1, 1)
            )
            
            editar_btn = WarningButton(text='EDITAR', size_hint_x=0.2)
            editar_btn.bind(on_press=lambda x, p=produto: self.editar_produto(p))
            
            excluir_btn = DangerButton(text='EXCLUIR', size_hint_x=0.2)
            excluir_btn.bind(on_press=lambda x, p=produto: self.excluir_produto(p))
            
            item.add_widget(info_label)
            item.add_widget(preco_label)
            item.add_widget(editar_btn)
            item.add_widget(excluir_btn)
            
            self.produtos_cadastrados.add_widget(item)

    def atualizar_lista_produtos_venda(self):
        # Se tem busca ativa, usa o filtro
        if hasattr(self, 'busca_input') and self.busca_input.text:
            self.filtrar_produtos_venda(None, self.busca_input.text)
            return
            
        self.produtos_grid.clear_widgets()
        
        if not self.produtos:
            self.produtos_grid.add_widget(
                Label(
                    text='Nenhum produto disponivel.\nCadastre produtos na aba "PRODUTOS".',
                    size_hint_y=None,
                    height=100
                )
            )
            return
        
        for produto in self.produtos:
            btn = StyledButton(
                text=f"{produto.nome}\n\nR$ {produto.preco:.2f}",
                size_hint_y=None,
                height=90
            )
            btn.bind(on_press=self.adicionar_ao_carrinho)
            self.produtos_grid.add_widget(btn)

    def adicionar_ao_carrinho(self, instance):
        produto = next(p for p in self.produtos if p.nome in instance.text)
        self.carrinho.append(produto)
        self.atualizar_total()
        self.atualizar_visualizacao_carrinho()
        self.mostrar_feedback_rapido(f"{produto.nome} adicionado!")

    def remover_do_carrinho(self, index):
        if 0 <= index < len(self.carrinho):
            produto_removido = self.carrinho.pop(index)
            self.atualizar_total()
            self.atualizar_visualizacao_carrinho()
            self.mostrar_feedback_rapido(f"{produto_removido.nome} removido!")

    def limpar_carrinho_completo(self, instance):
        if not self.carrinho:
            return
        
        self.carrinho.clear()
        self.atualizar_total()
        self.atualizar_visualizacao_carrinho()
        self.mostrar_feedback_rapido("Carrinho limpo!")

    def atualizar_visualizacao_carrinho(self):
        self.carrinho_grid.clear_widgets()
        
        if not self.carrinho:
            self.carrinho_grid.add_widget(
                Label(
                    text='Carrinho vazio\n\nSelecione produtos no cardapio',
                    size_hint_y=None,
                    height=100,
                    font_size='14sp'
                )
            )
            return
        
        for index, produto in enumerate(self.carrinho):
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
            
            # Nome e preco do produto
            info_label = Label(
                text=f"{produto.nome}",
                size_hint_x=0.6,
                font_size='15sp'
            )
            
            preco_label = Label(
                text=f"R$ {produto.preco:.2f}",
                size_hint_x=0.25,
                font_size='15sp',
                bold=True,
                color=(0.1, 0.5, 0.1, 1)
            )
            
            # Botao remover
            remover_btn = SmallDangerButton(
                text='X',
                size_hint_x=0.15
            )
            remover_btn.bind(on_press=lambda x, idx=index: self.remover_do_carrinho(idx))
            
            item.add_widget(info_label)
            item.add_widget(preco_label)
            item.add_widget(remover_btn)
            
            self.carrinho_grid.add_widget(item)

    def atualizar_total(self):
        total = sum(produto.preco for produto in self.carrinho)
        self.total_label.text = f'TOTAL: R$ {total:.2f}'

    def mostrar_feedback_rapido(self, mensagem):
        popup = Popup(
            title='',
            content=Label(text=mensagem, font_size='16sp'),
            size_hint=(0.6, 0.2),
            auto_dismiss=True
        )
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)

    def confirmar_venda(self, instance):
        if not self.carrinho:
            self.mostrar_popup("Atencao", "O carrinho esta vazio!\nAdicione produtos antes de finalizar.")
            return

        if self.forma_pagamento.text == 'Selecione...':
            self.mostrar_popup("Atencao", "Por favor, selecione a forma de pagamento!")
            return

        resumo = "=== RESUMO DA COMPRA ===\n\n"
        for i, produto in enumerate(self.carrinho, 1):
            resumo += f"{i}. {produto.nome}: R$ {produto.preco:.2f}\n"

        total = sum(produto.preco for produto in self.carrinho)
        resumo += f"\n{'_' * 30}\n"
        resumo += f"TOTAL: R$ {total:.2f}\n"
        resumo += f"Pagamento: {self.forma_pagamento.text}\n"

        if 'Dinheiro' in self.forma_pagamento.text:
            try:
                valor_recebido_str = self.pagamento_input.text.replace(',', '.')
                valor_recebido = float(valor_recebido_str)
                troco = valor_recebido - total
                if troco < 0:
                    self.mostrar_popup("Atencao", "Valor recebido insuficiente!")
                    return
                resumo += f"\nRecebido: R$ {valor_recebido:.2f}"
                resumo += f"\nTroco: R$ {troco:.2f}"
            except ValueError:
                self.mostrar_popup("Atencao", "Por favor, insira o valor recebido em dinheiro.")
                return

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=resumo, font_size='14sp'))

        botoes = BoxLayout(size_hint_y=None, height=60, spacing=10)
        popup = Popup(title='Confirmar Venda', content=content, size_hint=(0.9, 0.7))

        confirmar_btn = SuccessButton(text='CONFIRMAR VENDA')
        confirmar_btn.bind(on_press=lambda x: self.finalizar_venda(popup))
        
        cancelar_btn = DangerButton(text='CANCELAR')
        cancelar_btn.bind(on_press=popup.dismiss)

        botoes.add_widget(cancelar_btn)
        botoes.add_widget(confirmar_btn)
        content.add_widget(botoes)

        popup.open()

    def finalizar_venda(self, popup):
        popup.dismiss()
        total = sum(produto.preco for produto in self.carrinho)
        venda = {
            'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'produtos': [{'nome': p.nome, 'preco': p.preco} for p in self.carrinho],
            'total': total,
            'forma_pagamento': self.forma_pagamento.text
        }
        self.vendas.append(venda)
        self.salvar_vendas()

        mensagem = "VENDA FINALIZADA COM SUCESSO!\n\n"
        if 'Dinheiro' in self.forma_pagamento.text:
            valor_recebido_str = self.pagamento_input.text.replace(',', '.')
            valor_recebido = float(valor_recebido_str)
            troco = valor_recebido - total
            mensagem += f"Troco: R$ {troco:.2f}"

        self.mostrar_popup("Sucesso", mensagem)

        self.carrinho.clear()
        self.atualizar_total()
        self.atualizar_visualizacao_carrinho()
        self.pagamento_input.text = ''
        self.forma_pagamento.text = 'Selecione...'
        self.atualizar_historico()
        self.atualizar_relatorio()

    def cancelar_venda(self, instance):
        if not self.carrinho:
            return
            
        self.carrinho.clear()
        self.atualizar_total()
        self.atualizar_visualizacao_carrinho()
        self.pagamento_input.text = ''
        self.forma_pagamento.text = 'Selecione...'
        self.mostrar_popup("Venda Cancelada", "O carrinho foi limpo.")

    def atualizar_historico(self):
        if not hasattr(self, 'historico_grid') or self.historico_grid is None:
            return

        self.historico_grid.clear_widgets()
        
        # Atualizar titulo
        if hasattr(self, 'historico_titulo'):
            self.historico_titulo.text = f'Historico de Vendas ({len(self.vendas)})'
        
        if not self.vendas:
            self.historico_grid.add_widget(
                Label(
                    text='Nenhuma venda realizada ainda.',
                    size_hint_y=None,
                    height=100,
                    font_size='16sp'
                )
            )
            return

        for i, venda in enumerate(reversed(self.vendas)):
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=200, padding=10, spacing=5)
            
            # Cabecalho da venda
            header = BoxLayout(size_hint_y=None, height=30)
            header.add_widget(Label(
                text=f"Venda #{len(self.vendas)-i}",
                font_size='16sp',
                bold=True
            ))
            header.add_widget(Label(
                text=venda['data'],
                font_size='14sp'
            ))
            item.add_widget(header)
            
            # Itens com precos
            itens_text = "Itens comprados:\n"
            for produto in venda['produtos']:
                itens_text += f"  - {produto['nome']}: R$ {produto['preco']:.2f}\n"
            item.add_widget(Label(text=itens_text, font_size='13sp'))
            
            # Total e pagamento
            info_box = BoxLayout(size_hint_y=None, height=40)
            info_box.add_widget(Label(
                text=f"Total: R$ {venda['total']:.2f}",
                font_size='16sp',
                bold=True,
                color=(0.1, 0.5, 0.1, 1)
            ))
            info_box.add_widget(Label(
                text=venda['forma_pagamento'],
                font_size='14sp'
            ))
            item.add_widget(info_box)
            
            # Botao excluir
            excluir_btn = DangerButton(text='EXCLUIR VENDA', size_hint_y=None, height=40)
            excluir_btn.bind(on_press=lambda x, index=len(self.vendas)-i-1: self.excluir_venda(index))
            item.add_widget(excluir_btn)
            
            self.historico_grid.add_widget(item)

    def excluir_venda(self, index):
        del self.vendas[index]
        self.salvar_vendas()
        self.atualizar_historico()
        self.atualizar_relatorio()

    def mostrar_popup(self, titulo, mensagem):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=mensagem, font_size='16sp'))
        
        fechar_btn = StyledButton(text='FECHAR', size_hint_y=None, height=50)
        content.add_widget(fechar_btn)

        popup = Popup(title=titulo, content=content, size_hint=(0.8, 0.5))
        fechar_btn.bind(on_press=popup.dismiss)
        popup.open()

    def salvar_produtos(self):
        with open('produtos.json', 'w', encoding='utf-8') as f:
            json.dump([{'nome': p.nome, 'preco': p.preco} for p in self.produtos], f, ensure_ascii=False)

    def carregar_produtos(self):
        if os.path.exists('produtos.json'):
            with open('produtos.json', 'r', encoding='utf-8') as f:
                produtos_data = json.load(f)
                self.produtos = [Produto(p['nome'], p['preco']) for p in produtos_data]

    def salvar_vendas(self):
        with open('vendas.json', 'w', encoding='utf-8') as f:
            json.dump(self.vendas, f, ensure_ascii=False)

    def carregar_vendas(self):
        if os.path.exists('vendas.json'):
            with open('vendas.json', 'r', encoding='utf-8') as f:
                self.vendas = json.load(f)

    def atualizar_relatorio(self):
        self.relatorio_grid.clear_widgets()

        if not self.vendas:
            self.relatorio_grid.add_widget(
                Label(
                    text='Nenhuma venda registrada para gerar relatorio.',
                    size_hint_y=None,
                    height=100,
                    font_size='16sp'
                )
            )
            return

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

        # Cabecalho
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=5)
        header.add_widget(Label(text='Produto', font_size='16sp', bold=True))
        header.add_widget(Label(text='Qtd Vendida', font_size='16sp', bold=True))
        header.add_widget(Label(text='Total', font_size='16sp', bold=True))
        self.relatorio_grid.add_widget(header)

        # Produtos
        for nome_produto, dados in sorted(produto_vendas.items(), key=lambda x: x[1]['total'], reverse=True):
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=5)
            item.add_widget(Label(text=nome_produto, font_size='15sp'))
            item.add_widget(Label(text=str(dados['quantidade']), font_size='15sp'))
            item.add_widget(Label(
                text=f"R$ {dados['total']:.2f}",
                font_size='15sp',
                bold=True,
                color=(0.1, 0.5, 0.1, 1)
            ))
            self.relatorio_grid.add_widget(item)

        # Total geral
        separator = Label(text='=' * 50, size_hint_y=None, height=30)
        self.relatorio_grid.add_widget(separator)
        
        total_label = Label(
            text=f"TOTAL GERAL: R$ {total_vendas:.2f}",
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True,
            color=(0.1, 0.5, 0.1, 1)
        )
        self.relatorio_grid.add_widget(total_label)

if __name__ == '__main__':
    CaixaApp().run()
