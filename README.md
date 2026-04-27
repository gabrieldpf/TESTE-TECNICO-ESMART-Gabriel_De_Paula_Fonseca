# Galeria Pexels Desktop (PySide6)

Aplicacao desktop em Python com PySide6 para listar fotos da API do Pexels com paginacao, visualizacao de detalhes e exportacao CSV.

## Requisitos

- Python 3.9+
- Chave de API do Pexels ([https://www.pexels.com/api/](https://www.pexels.com/api/))

## Configuracao

1. Clone/abra o projeto.
2. Crie e edite o arquivo `.env` na raiz:

```env
PEXELS_API_KEY=COLE_SUA_CHAVE_AQUI
```

3. Instale dependencias:

```bash
pip install -r requirements.txt
```

## Como executar

```bash
python main.py
```

Se a chave nao estiver configurada, a aplicacao exibe erro amigavel informando como corrigir.

## Funcionalidades

- **Listagem inicial:** carrega 20 fotos de `/v1/curated`
- **Grid responsivo com scroll vertical**
- **Cards** com imagem (`src.medium`), fotografo e efeito hover
- **Paginacao:** botao `Carregar mais`, mantendo fotos ja carregadas
- **Detalhes em dialog:** imagem maior, `alt`, `width`, `height`, `photographer`, `photographer_url`
- **Exportacao CSV:** `id`, `alt`, `width`, `height`, `photographer`, `photographer_url`
- **Extras:** loading spinner, placeholder de imagem, abertura de links via `webbrowser.open`

## Arquitetura

```
project/
├── main.py                    # bootstrap da aplicacao
├── config.py                  # leitura segura da API key via env
├── services/
│   └── pexels_service.py      # integracao com API Pexels e tratamento de erros
├── ui/
│   ├── main_window.py         # janela principal, grid, paginacao e exportacao
│   ├── components/
│   │   └── card.py            # componente visual do card + carregamento async de imagem
│   └── dialogs/
│       └── photo_dialog.py    # dialog de detalhes da foto + link clicavel
├── utils/
│   └── exporter.py            # utilitario para gerar CSV
└── .env                       # configuracao local (nao versionar)
```

## Seguranca

- A chave da API **nao** esta hardcoded.
- `config.py` carrega `.env` e usa `os.getenv("PEXELS_API_KEY")`.
- Em ausencia da chave, a aplicacao interrompe de forma controlada com mensagem explicativa.
